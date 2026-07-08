"""
Anthropic Batch-API runner (50% cost) for the API evaluation — Claude models.
Builds ONE batch covering all requested (model,slug) pairs × all suites
(core ED/Strict/Normalcy + SP + SC[k] + RAG), submits, polls, reconstructs
per-suite result files in the SAME schema as run_open_models.py.

LP is intentionally excluded (Claude does not expose token logprobs).
RAG embeddings use OpenAI text-embedding-3-small (shared across all API runs so
retrieved neighbours are identical to the GPT runs).

Usage (ANTHROPIC_API_KEY + OPENAI_API_KEY must be in env):
    OPENWEIGHT_OUTDIR=results_api python run_claude_batch.py \
        claude-opus-4-8:claude_opus_4_8 claude-sonnet-4-6:claude_sonnet_4_6
"""
import os, sys, json, time, math
os.environ.setdefault("OPENWEIGHT_PROVIDER", "openai")   # R.client = OpenAI (for embeddings)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_open_models as R
from prompts_core import METHODS, BASELINE_SINGLE, SC_BASE_PROMPT, RAG_BASE_PROMPT, RAG_K
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

ac = anthropic.Anthropic()
SC_K = int(os.environ.get("OPENWEIGHT_SC_K", "5"))
MAXTOK = int(os.environ.get("OPENWEIGHT_CLAUDE_MAXTOK", "6000"))


def params(model, system, text):
    return MessageCreateParamsNonStreaming(
        model=model, max_tokens=MAXTOK, system=system,
        messages=[{"role": "user", "content": f"Analyze the following construction report excerpt:\n\n{text}"}])


def build(models, cases):
    reqs, rag_nb = [], {}
    embs = R._embed(R.EMBED_MODEL_DEFAULT, [c["text"] for c in cases])

    def cos(a, b):
        s = sum(x*y for x, y in zip(a, b)); na = math.sqrt(sum(x*x for x in a)) or 1; nb = math.sqrt(sum(y*y for y in b)) or 1
        return s/(na*nb)
    for model, slug in models:
        singles = dict(METHODS); singles.update(BASELINE_SINGLE)
        for mk, mi in singles.items():
            for c in cases:
                reqs.append(Request(custom_id=f"{slug}-{mk}-{c['id']}-0", params=params(model, mi["prompt"], c["text"])))
        for c in cases:
            for i in range(SC_K):
                reqs.append(Request(custom_id=f"{slug}-sc-{c['id']}-{i}", params=params(model, SC_BASE_PROMPT, c["text"])))
        for i, c in enumerate(cases):
            sims = sorted(((j, cos(embs[i], embs[j])) for j in range(len(cases)) if j != i), key=lambda t: -t[1])[:RAG_K]
            shots = "\n\n".join(f"Example {n+1} (label: {cases[j]['gold_label']}):\n{cases[j]['text']}" for n, (j, _) in enumerate(sims))
            rag_nb[(slug, c["id"])] = [cases[j]["id"] for j, _ in sims]
            reqs.append(Request(custom_id=f"{slug}-rag-{c['id']}-0",
                                params=params(model, RAG_BASE_PROMPT + "\n\n- Retrieved similar labeled examples (for reference)\n" + shots, c["text"])))
    return reqs, rag_nb


def submit_and_wait(reqs):
    b = ac.messages.batches.create(requests=reqs)
    print(f"submitted Claude batch {b.id} ({len(reqs)} requests); polling...")
    while True:
        b = ac.messages.batches.retrieve(b.id)
        rc = b.request_counts
        print(f"  {b.processing_status} succeeded={rc.succeeded} errored={rc.errored} processing={rc.processing}")
        if b.processing_status == "ended":
            break
        time.sleep(60)
    res = {}
    for r in ac.messages.batches.results(b.id):
        if r.result.type == "succeeded":
            msg = r.result.message
            txt = "".join(blk.text for blk in msg.content if blk.type == "text")
            res[r.custom_id] = {"content": txt, "usage": {"prompt_tokens": msg.usage.input_tokens, "completion_tokens": msg.usage.output_tokens, "total_tokens": msg.usage.input_tokens + msg.usage.output_tokens}, "model": msg.model}
        else:
            res[r.custom_id] = {"content": None, "usage": {}, "model": "", "err": r.result.type}
    return res


def reconstruct(res, models, cases, rag_nb):
    from collections import Counter
    cmap = {c["id"]: c for c in cases}

    def rec(slug, mk, cid):
        r = res.get(f"{slug}-{mk}-{cid}-0", {})
        return {"response": R.extract_json(r["content"]) if r.get("content") else {"parse_error": True},
                "usage": r.get("usage", {}), "model": r.get("model", ""),
                "case_id": cid, "gold_label": cmap[cid]["gold_label"], "category": cmap[cid]["category"]}
    for model, slug in models:
        combined = {}
        for mk in list(METHODS) + list(BASELINE_SINGLE):
            rows = [rec(slug, mk, c["id"]) for c in cases]
            json.dump(rows, open(R.OUTDIR / f"{slug}__{mk}.json", "w"), indent=2, ensure_ascii=False)
            combined[mk] = rows
        sc_rows = []
        for c in cases:
            samples = [R._norm(R.extract_json(res.get(f"{slug}-sc-{c['id']}-{i}", {}).get("content") or "").get("label")) for i in range(SC_K)]
            votes = Counter(s for s in samples if s not in ("ERROR", "PARSE_ERROR"))
            top, agree = (votes.most_common(1)[0][0], votes.most_common(1)[0][1]/SC_K) if votes else ("PARSE_ERROR", 0.0)
            sc_rows.append({"response": {"label": top}, "sc_samples": samples, "sc_votes": dict(votes), "sc_agreement": agree,
                            "case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"]})
        json.dump(sc_rows, open(R.OUTDIR / f"{slug}__sc.json", "w"), indent=2, ensure_ascii=False); combined["sc"] = sc_rows
        rag_rows = []
        for c in cases:
            row = rec(slug, "rag", c["id"]); row["rag_neighbors"] = rag_nb.get((slug, c["id"]), []); rag_rows.append(row)
        json.dump(rag_rows, open(R.OUTDIR / f"{slug}__rag.json", "w"), indent=2, ensure_ascii=False); combined["rag"] = rag_rows
        json.dump(combined, open(R.OUTDIR / f"{slug}__all.json", "w"), indent=2, ensure_ascii=False)
        print(f"reconstructed {slug}: {sorted(combined.keys())}")


if __name__ == "__main__":
    models = [tuple(a.split(":")) for a in sys.argv[1:]]   # ["model:slug", ...]
    cases = json.load(open(R.DATASET))["cases"]
    reqs, rag_nb = build(models, cases)
    res = submit_and_wait(reqs)
    reconstruct(res, models, cases, rag_nb)

"""
OpenAI Batch-API runner (50% cost) for the API evaluation — used for expensive
flagship models (e.g. gpt-5.5). Builds ONE batch covering all suites
(core ED/Strict/Normalcy + SP + SC[k] + RAG), submits, polls, then reconstructs
per-suite result files in the SAME schema as run_open_models.py so analyze_open.py
works unchanged. RAG embeddings are computed synchronously (cheap, not the cost driver).

Usage:
    python run_openai_batch.py <openai_model> <slug>
    e.g. OPENWEIGHT_OUTDIR=results_api python run_openai_batch.py gpt-5.5 gpt_5_5
"""
import os, sys, json, time, math
os.environ.setdefault("OPENWEIGHT_PROVIDER", "openai")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_open_models as R          # provides client (OpenAI), extract_json, _norm, MAX_TOKENS, DATASET, OUTDIR, prompts
from prompts_core import METHODS, BASELINE_SINGLE, SC_BASE_PROMPT, RAG_BASE_PROMPT, RAG_K, EMBED_MODEL_DEFAULT

EFFORT = os.environ.get("OPENWEIGHT_OPENAI_EFFORT", "high")
SC_K = int(os.environ.get("OPENWEIGHT_SC_K", "5"))


def body(model, system, text):
    return {"model": model, "max_completion_tokens": R.MAX_TOKENS, "reasoning_effort": EFFORT,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": f"Analyze the following construction report excerpt:\n\n{text}"}]}


def build_requests(model, cases):
    reqs, rag_neighbors = [], {}
    # single-pass: core + sp
    singles = dict(METHODS); singles.update(BASELINE_SINGLE)
    for mk, mi in singles.items():
        for c in cases:
            reqs.append({"custom_id": f"{mk}__{c['id']}__0", "method": "POST",
                         "url": "/v1/chat/completions", "body": body(model, mi["prompt"], c["text"])})
    # SC: k samples of the ED prompt
    for c in cases:
        for i in range(SC_K):
            reqs.append({"custom_id": f"sc__{c['id']}__{i}", "method": "POST",
                         "url": "/v1/chat/completions", "body": body(model, SC_BASE_PROMPT, c["text"])})
    # RAG: leave-one-out top-k neighbours as few-shot (embeddings computed sync).
    # Use R.EMBED_MODEL_DEFAULT (set to an OpenAI embedding model in openai mode).
    embs = R._embed(R.EMBED_MODEL_DEFAULT, [c["text"] for c in cases])

    def cos(a, b):
        s = sum(x * y for x, y in zip(a, b)); na = math.sqrt(sum(x * x for x in a)) or 1.0; nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return s / (na * nb)
    for i, c in enumerate(cases):
        sims = sorted(((j, cos(embs[i], embs[j])) for j in range(len(cases)) if j != i), key=lambda t: -t[1])[:RAG_K]
        shots = "\n\n".join(f"Example {n+1} (label: {cases[j]['gold_label']}):\n{cases[j]['text']}" for n, (j, _) in enumerate(sims))
        rag_neighbors[c["id"]] = [cases[j]["id"] for j, _ in sims]
        reqs.append({"custom_id": f"rag__{c['id']}__0", "method": "POST", "url": "/v1/chat/completions",
                     "body": body(model, RAG_BASE_PROMPT + "\n\n## Retrieved similar labeled examples (for reference)\n" + shots, c["text"])})
    return reqs, rag_neighbors


def submit_and_wait(reqs, slug):
    path = R.OUTDIR / f"{slug}__batch_input.jsonl"
    with open(path, "w") as f:
        for r in reqs:
            f.write(json.dumps(r) + "\n")
    up = R.client.files.create(file=open(path, "rb"), purpose="batch")
    batch = R.client.batches.create(input_file_id=up.id, endpoint="/v1/chat/completions", completion_window="24h")
    print(f"submitted batch {batch.id} ({len(reqs)} requests); polling...")
    (R.OUTDIR / f"{slug}__batch_id.txt").write_text(batch.id)
    while True:
        b = R.client.batches.retrieve(batch.id)
        rc = b.request_counts
        print(f"  status={b.processing_status if hasattr(b,'processing_status') else b.status} "
              f"completed={getattr(rc,'completed',0)}/{getattr(rc,'total',0)} failed={getattr(rc,'failed',0)}")
        if b.status in ("completed", "failed", "expired", "cancelled"):
            break
        time.sleep(60)
    if b.status != "completed":
        print(f"BATCH {b.status}; error_file={b.error_file_id}");
        if b.error_file_id:
            print(R.client.files.content(b.error_file_id).text[:2000])
        sys.exit(1)
    out = R.client.files.content(b.output_file_id).text
    res = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        cid = o["custom_id"]
        resp = o.get("response", {}).get("body", {})
        try:
            content = resp["choices"][0]["message"]["content"]
        except Exception:
            content = None
        res[cid] = {"content": content, "usage": resp.get("usage", {}), "model": resp.get("model", "")}
    return res


def reconstruct(res, slug, cases, rag_neighbors):
    cmap = {c["id"]: c for c in cases}
    combined = {}

    def rec(cid, content, usage, model):
        return {"response": R.extract_json(content) if content else {"parse_error": True},
                "usage": {"prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                          "total_tokens": usage.get("total_tokens")}, "model": model,
                "case_id": cid, "gold_label": cmap[cid]["gold_label"], "category": cmap[cid]["category"]}

    for mk in list(METHODS) + list(BASELINE_SINGLE):
        rows = []
        for c in cases:
            k = f"{mk}__{c['id']}__0"; r = res.get(k, {})
            rows.append(rec(c["id"], r.get("content"), r.get("usage", {}), r.get("model", "")))
        json.dump(rows, open(R.OUTDIR / f"{slug}__{mk}.json", "w"), indent=2, ensure_ascii=False)
        combined[mk] = rows
    # SC
    from collections import Counter
    sc_rows = []
    for c in cases:
        samples = []
        for i in range(SC_K):
            r = res.get(f"sc__{c['id']}__{i}", {})
            lbl = R._norm(R.extract_json(r["content"]).get("label")) if r.get("content") else "ERROR"
            samples.append(lbl)
        votes = Counter(s for s in samples if s not in ("ERROR", "PARSE_ERROR"))
        top, agree = (votes.most_common(1)[0][0], votes.most_common(1)[0][1] / SC_K) if votes else ("PARSE_ERROR", 0.0)
        sc_rows.append({"response": {"label": top}, "sc_samples": samples, "sc_votes": dict(votes),
                        "sc_agreement": agree, "case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"]})
    json.dump(sc_rows, open(R.OUTDIR / f"{slug}__sc.json", "w"), indent=2, ensure_ascii=False)
    combined["sc"] = sc_rows
    # RAG
    rag_rows = []
    for c in cases:
        r = res.get(f"rag__{c['id']}__0", {})
        row = rec(c["id"], r.get("content"), r.get("usage", {}), r.get("model", ""))
        row["rag_neighbors"] = rag_neighbors.get(c["id"], [])
        rag_rows.append(row)
    json.dump(rag_rows, open(R.OUTDIR / f"{slug}__rag.json", "w"), indent=2, ensure_ascii=False)
    combined["rag"] = rag_rows
    json.dump(combined, open(R.OUTDIR / f"{slug}__all.json", "w"), indent=2, ensure_ascii=False)
    print(f"reconstructed {slug}: {sorted(combined.keys())} -> {R.OUTDIR}")


if __name__ == "__main__":
    model, slug = sys.argv[1], sys.argv[2]
    cases = json.load(open(R.DATASET))["cases"]
    reqs, rag_neighbors = build_requests(model, cases)
    res = submit_and_wait(reqs, slug)
    reconstruct(res, slug, cases, rag_neighbors)

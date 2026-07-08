"""
Open-weight core comparison runner (IEEE Access resubmission).

Runs the three core decision configurations — Original (Extract-then-Decide),
Strict EC, and Normalcy EC — on dataset_v2.json (40 construction cases) through
a local open-weight model served by Ollama's OpenAI-compatible endpoint.

Usage:
    python run_open_models.py <ollama_model_tag> [output_slug]
    e.g. python run_open_models.py gemma3:27b gemma3_27b

Prompts are reused verbatim from the original GPT experiments so that the only
variable is the model. Results are saved per (model, method) in ./results/ using
the same JSON schema as the original results/ directory.
"""

import json
import re
import sys
import time
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).resolve().parent
# Prefer the portable bundle copy; fall back to the parent florence repo.
DATASET = HERE / "dataset_v2.json"
if not DATASET.exists():
    DATASET = HERE.parent / "dataset_v2.json"
import os  # noqa: E402
OUTDIR = Path(os.environ.get("OPENWEIGHT_OUTDIR", HERE / "results"))
OUTDIR.mkdir(parents=True, exist_ok=True)

# Self-contained prompts (portable). Falls back to parent repo if missing.
sys.path.insert(0, str(HERE))
from prompts_core import (  # noqa: E402
    METHODS, BASELINE_SINGLE, SC_BASE_PROMPT,
    LP_PROMPT, LP_LABEL_TOKENS, EMBED_MODEL_DEFAULT, RAG_K, RAG_BASE_PROMPT,
)

# Provider: "ollama" (local, default) or "openai" (real OpenAI API for gpt-* models).
# Auto-detect OpenAI when the model tag looks like a GPT model, unless overridden.
PROVIDER = os.environ.get("OPENWEIGHT_PROVIDER", "")
if not PROVIDER:
    PROVIDER = "openai" if any(("gpt-" in a or "gpt_" in a) for a in sys.argv[1:2]) else "ollama"

if PROVIDER == "openai":
    try:
        from dotenv import load_dotenv  # best-effort .env load for OPENAI_API_KEY
        for p in (HERE.parent / ".env", HERE / ".env"):
            if p.exists():
                load_dotenv(p)
    except Exception:
        pass
    client = OpenAI()                       # uses OPENAI_API_KEY from env
    OPENAI_EFFORT = os.environ.get("OPENWEIGHT_OPENAI_EFFORT", "high")
    EMBED_MODEL_DEFAULT = os.environ.get("OPENWEIGHT_EMBED_MODEL", "text-embedding-3-small")
else:
    BASE_URL = os.environ.get("OLLAMA_OPENAI_BASE", "http://127.0.0.1:11434/v1")
    client = OpenAI(base_url=BASE_URL, api_key="ollama")
    OPENAI_EFFORT = None


def strip_think(s: str) -> str:
    """Remove <think>...</think> blocks emitted by reasoning models."""
    return re.sub(r"<think>.*?</think>", "", s, flags=re.DOTALL)


def extract_json(content: str) -> dict:
    s = strip_think(content or "").strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    # balanced-brace scan: first '{' to its matching '}' (handles trailing junk / extra braces)
    start = s.find("{")
    if start != -1:
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i + 1])
                    except Exception:
                        break
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"raw": content, "parse_error": True}


MAX_TOKENS = int(os.environ.get("OPENWEIGHT_MAX_TOKENS", "16384"))


def call(model: str, system: str, text: str, temperature: float = 0.0) -> dict:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Analyze the following construction report excerpt:\n\n{text}"},
    ]
    if PROVIDER == "openai":
        # GPT-5.x reasoning models: max_completion_tokens + reasoning_effort, no temperature.
        kwargs = dict(model=model, max_completion_tokens=MAX_TOKENS, messages=messages,
                      response_format={"type": "json_object"})
        if OPENAI_EFFORT:
            kwargs["reasoning_effort"] = OPENAI_EFFORT
        r = client.chat.completions.create(**kwargs)
    else:
        r = client.chat.completions.create(
            model=model, temperature=temperature, max_tokens=MAX_TOKENS, messages=messages,
            response_format={"type": "json_object"},
        )
    parsed = extract_json(r.choices[0].message.content)
    return {
        "response": parsed,
        "usage": {
            "prompt_tokens": r.usage.prompt_tokens,
            "completion_tokens": r.usage.completion_tokens,
            "total_tokens": r.usage.total_tokens,
        },
        "model": r.model,
        "finish_reason": r.choices[0].finish_reason,
    }


# Self-consistency parameters (configurable via env).
SC_K = int(os.environ.get("OPENWEIGHT_SC_K", "5"))
SC_TEMP = float(os.environ.get("OPENWEIGHT_SC_TEMP", "0.7"))
# LP needs enough tokens for reasoning models to finish thinking and emit the label.
LP_MAXTOK = int(os.environ.get("OPENWEIGHT_LP_MAXTOK", "2048"))


def _norm(label) -> str:
    if not label:
        return "PARSE_ERROR"
    l = str(label).strip().lower()
    if "uncertain" in l or "abstain" in l:
        return "Uncertain"
    if "no delay" in l or "no_delay" in l or "nodelay" in l or "no impact" in l:
        return "No Delay"
    if "delay" in l:
        return "Delay"
    return str(label)


def run_single(model_tag: str, slug: str, methods: dict):
    """Single-pass methods (core EC configs and SP), temperature 0."""
    cases = json.load(open(DATASET))["cases"]
    all_results = {}
    for mk, mi in methods.items():
        print(f"\n=== {mi['name']} ({mk}) | model={model_tag} ===")
        res = []
        for i, c in enumerate(cases, 1):
            t0 = time.time()
            try:
                out = call(model_tag, mi["prompt"], c["text"], temperature=0.0)
                lbl = out["response"].get("label", "PARSE_ERROR")
            except Exception as e:
                out = {"error": str(e)}
                lbl = f"ERROR: {e}"
            out.update({"case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"]})
            res.append(out)
            print(f"  [{i:2d}/{len(cases)}] {c['id']} (gold={c['gold_label']}) -> {lbl}  ({time.time()-t0:.1f}s)")
        all_results[mk] = res
        json.dump(res, open(OUTDIR / f"{slug}__{mk}.json", "w"), indent=2, ensure_ascii=False)
    return all_results


def run_sc(model_tag: str, slug: str, k: int = SC_K, temp: float = SC_TEMP):
    """Self-consistency: sample the ED prompt k times at temp, majority vote."""
    from collections import Counter
    cases = json.load(open(DATASET))["cases"]
    res = []
    print(f"\n=== Self-Consistency (sc, k={k}, T={temp}) | model={model_tag} ===")
    for i, c in enumerate(cases, 1):
        t0 = time.time()
        samples = []
        for _ in range(k):
            try:
                out = call(model_tag, SC_BASE_PROMPT, c["text"], temperature=temp)
                samples.append(_norm(out["response"].get("label")))
            except Exception as e:
                samples.append(f"ERROR")
        votes = Counter(s for s in samples if s not in ("ERROR", "PARSE_ERROR"))
        if votes:
            top, n = votes.most_common(1)[0]
            agreement = n / k
        else:
            top, agreement = "PARSE_ERROR", 0.0
        rec = {
            "response": {"label": top},          # majority label (SC-vote)
            "sc_samples": samples,
            "sc_votes": dict(votes),
            "sc_agreement": agreement,            # max votes / k -> used for SC-abstain curve
            "case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"],
        }
        res.append(rec)
        print(f"  [{i:2d}/{len(cases)}] {c['id']} (gold={c['gold_label']}) -> {top} (agree={agreement:.2f}) {dict(votes)}  ({time.time()-t0:.1f}s)")
    json.dump(res, open(OUTDIR / f"{slug}__sc.json", "w"), indent=2, ensure_ascii=False)
    return res


def run_lp(model_tag: str, slug: str):
    """LP: constrained single-token label with logprob-based confidence."""
    cases = json.load(open(DATASET))["cases"]
    res = []
    print(f"\n=== Logprob Uncertainty (lp) | model={model_tag} ===")
    for i, c in enumerate(cases, 1):
        t0 = time.time()
        label, conf, dist = "PARSE_ERROR", None, {}
        try:
            import math
            # Reasoning models emit a <think>...</think> trace before the label. We give them
            # room to finish thinking (large max_tokens) and then read the label token that
            # appears AFTER the last </think>. Non-reasoning models emit the label at position 0.
            user_msg = f"Excerpt:\n\n{c['text']}\n\nLabel:"
            extra = {"think": False}
            if "qwen3" in model_tag:
                user_msg += " /no_think"            # Qwen3 native thinking-off switch
            if "gpt-oss" in model_tag:
                extra["reasoning_effort"] = "low"
            r = client.chat.completions.create(
                model=model_tag, temperature=0, max_tokens=LP_MAXTOK,
                logprobs=True, top_logprobs=10,
                extra_body=extra,
                messages=[{"role": "system", "content": LP_PROMPT},
                          {"role": "user", "content": user_msg}],
            )
            toks = (r.choices[0].logprobs.content if r.choices[0].logprobs else None) or []
            # start scanning after the last </think> marker (if any), else from the top
            start = 0
            for idx, t in enumerate(toks):
                if "</think>" in t.token:
                    start = idx + 1
            # take the LAST label token in the answer region (= the committed final label;
            # avoids picking a label word mentioned mid-reasoning)
            chosen = None
            for t in toks[start:]:
                key = t.token.strip().lower().lstrip("`").rstrip("`")
                if key in LP_LABEL_TOKENS:
                    chosen = t
            if chosen is not None:
                label = LP_LABEL_TOKENS[chosen.token.strip().lower().lstrip("`").rstrip("`")]
                cand = {}
                for x in (chosen.top_logprobs or [chosen]):
                    k = x.token.strip().lower().lstrip("`").rstrip("`")
                    if k in LP_LABEL_TOKENS:
                        cand[LP_LABEL_TOKENS[k]] = cand.get(LP_LABEL_TOKENS[k], 0.0) + math.exp(x.logprob)
                Z = sum(cand.values()) or 1.0
                dist = {k: v / Z for k, v in cand.items()}
                conf = dist.get(label, math.exp(chosen.logprob))
        except Exception as e:
            label, conf = f"ERROR", None
            dist = {"error": str(e)}
        rec = {"response": {"label": label, "confidence": (round(conf * 100, 1) if conf is not None else None)},
               "lp_label_dist": dist, "case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"]}
        res.append(rec)
        print(f"  [{i:2d}/{len(cases)}] {c['id']} (gold={c['gold_label']}) -> {label} (conf={rec['response']['confidence']})  ({time.time()-t0:.1f}s)")
    json.dump(res, open(OUTDIR / f"{slug}__lp.json", "w"), indent=2, ensure_ascii=False)
    return res


def _embed(model: str, texts):
    r = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in r.data]


def run_rag(model_tag: str, slug: str, k: int = RAG_K, embed_model: str = None,
            exclude_same_category: bool = False, out_key: str = "rag"):
    """RAG: retrieve top-k similar cases as few-shot, then classify.

    exclude_same_category=True → leave-one-category-out (LOCO): the retrieval pool
    excludes cases sharing the test case's category, simulating a *novel/unknown
    risk factor* with no labeled precedent.
    """
    import math
    embed_model = embed_model or os.environ.get("OPENWEIGHT_EMBED_MODEL", EMBED_MODEL_DEFAULT)
    cases = json.load(open(DATASET))["cases"]
    embs = _embed(embed_model, [c["text"] for c in cases])

    def cos(a, b):
        s = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return s / (na * nb)

    res = []
    print(f"\n=== Retrieval-Augmented ICL ({out_key}, k={k}, embed={embed_model}, LOCO={exclude_same_category}) | model={model_tag} ===")
    for i, c in enumerate(cases, 1):
        t0 = time.time()
        pool = [j for j in range(len(cases)) if j != i - 1
                and not (exclude_same_category and cases[j]["category"] == c["category"])]
        sims = sorted(((j, cos(embs[i - 1], embs[j])) for j in pool), key=lambda t: -t[1])[:k]
        shots = "\n\n".join(
            f"Example {n+1} (label: {cases[j]['gold_label']}):\n{cases[j]['text']}" for n, (j, _) in enumerate(sims))
        sys_p = RAG_BASE_PROMPT + "\n\n## Retrieved similar labeled examples (for reference)\n" + shots
        try:
            out = call(model_tag, sys_p, c["text"], temperature=0.0)
            lbl = out["response"].get("label", "PARSE_ERROR")
        except Exception as e:
            out = {"error": str(e)}; lbl = "ERROR"
        out.update({"case_id": c["id"], "gold_label": c["gold_label"], "category": c["category"],
                    "rag_neighbors": [cases[j]["id"] for j, _ in sims],
                    "rag_neighbor_labels": [cases[j]["gold_label"] for j, _ in sims]})
        res.append(out)
        print(f"  [{i:2d}/{len(cases)}] {c['id']} (gold={c['gold_label']}) -> {lbl}  nn={[cases[j]['id'] for j,_ in sims]}  ({time.time()-t0:.1f}s)")
    json.dump(res, open(OUTDIR / f"{slug}__{out_key}.json", "w"), indent=2, ensure_ascii=False)
    return res


def run(model_tag: str, slug: str, suite: str = "all"):
    # Merge into any existing __all.json so suites can be run separately.
    all_path = OUTDIR / f"{slug}__all.json"
    combined = json.load(open(all_path)) if all_path.exists() else {}
    if suite in ("all", "core"):
        combined.update(run_single(model_tag, slug, METHODS))
    if suite == "strict":   # re-run only the (corrected) Strict EC config
        combined.update(run_single(model_tag, slug, {"strict_ec": METHODS["strict_ec"]}))
    if suite in ("all", "sp"):
        combined.update(run_single(model_tag, slug, BASELINE_SINGLE))
    if suite in ("all", "sc"):
        combined["sc"] = run_sc(model_tag, slug)
    if suite in ("all", "v2", "lp"):
        combined["lp"] = run_lp(model_tag, slug)
    if suite in ("all", "v2", "rag"):
        combined["rag"] = run_rag(model_tag, slug)
    if suite in ("rag_loco", "loco"):
        combined["rag_loco"] = run_rag(model_tag, slug, exclude_same_category=True, out_key="rag_loco")
    json.dump(combined, open(all_path, "w"), indent=2, ensure_ascii=False)
    print(f"\nSaved results for {slug} (suite={suite}) to {OUTDIR}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python run_open_models.py <ollama_model_tag> [output_slug] [suite=all|core|sp|sc]")
        sys.exit(1)
    tag = sys.argv[1]
    slug = sys.argv[2] if len(sys.argv) > 2 else tag.replace(":", "_").replace("/", "_").replace(".", "_")
    suite = sys.argv[3] if len(sys.argv) > 3 else "all"
    run(tag, slug, suite)

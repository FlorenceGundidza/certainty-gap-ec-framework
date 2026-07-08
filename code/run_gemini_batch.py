"""
Gemini Batch-API runner (50% cost) for the API evaluation — one batch per model
(model is batch-level in google-genai). Covers all suites (core + SP + SC[k] + RAG),
reconstructs per-suite files in the standard schema. LP excluded (no logprobs).
RAG embeddings via OpenAI text-embedding-3-small (shared with the GPT/Claude runs).

Usage (GOOGLE_API_KEY + OPENAI_API_KEY in env):
    OPENWEIGHT_OUTDIR=results_api python run_gemini_batch.py \
        gemini-3.5-flash:gemini_3_5_flash gemini-2.5-pro:gemini_2_5_pro gemini-3.1-pro-preview:gemini_3_1_pro
"""
import os, sys, json, time, math
os.environ.setdefault("OPENWEIGHT_PROVIDER", "openai")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_open_models as R
from prompts_core import METHODS, BASELINE_SINGLE, SC_BASE_PROMPT, RAG_BASE_PROMPT, RAG_K
from google import genai
from google.genai import types

gc = genai.Client()
SC_K = int(os.environ.get("OPENWEIGHT_SC_K", "5"))


def cfg(system, temperature):
    return types.GenerateContentConfig(system_instruction=system, response_mime_type="application/json",
                                       temperature=temperature)


def build_for_model(cases, embs):
    """Return (src_list, meta_list) in matching order for one model."""
    src, meta = [], []
    def add(mk, cid, i, system, text, temp):
        src.append(types.InlinedRequest(contents=f"Analyze the following construction report excerpt:\n\n{text}",
                                         config=cfg(system, temp), metadata={"k": f"{mk}-{cid}-{i}"}))
        meta.append((mk, cid, i))
    singles = dict(METHODS); singles.update(BASELINE_SINGLE)
    for mk, mi in singles.items():
        for c in cases: add(mk, c["id"], 0, mi["prompt"], c["text"], 0.0)
    for c in cases:
        for i in range(SC_K): add("sc", c["id"], i, SC_BASE_PROMPT, c["text"], 1.0)
    def cos(a, b):
        s=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)) or 1; nb=math.sqrt(sum(y*y for y in b)) or 1; return s/(na*nb)
    rag_nb = {}
    for i, c in enumerate(cases):
        sims = sorted(((j, cos(embs[i], embs[j])) for j in range(len(cases)) if j != i), key=lambda t:-t[1])[:RAG_K]
        shots = "\n\n".join(f"Example {n+1} (label: {cases[j]['gold_label']}):\n{cases[j]['text']}" for n,(j,_) in enumerate(sims))
        rag_nb[c["id"]] = [cases[j]["id"] for j,_ in sims]
        add("rag", c["id"], 0, RAG_BASE_PROMPT + "\n\nRetrieved similar labeled examples (for reference)\n" + shots, c["text"], 0.0)
    return src, meta, rag_nb


def resp_text(r):
    try: return r.text or ""
    except Exception:
        try: return "".join(p.text for p in r.candidates[0].content.parts if getattr(p, "text", None))
        except Exception: return ""


def reconstruct(slug, cases, results_by_meta, rag_nb):
    from collections import Counter
    cmap={c["id"]:c for c in cases}; combined={}
    def rec(mk,cid):
        d=results_by_meta.get((mk,cid,0),{})
        return {"response": R.extract_json(d.get("text") or "") if d.get("text") else {"parse_error":True},
                "usage": d.get("usage",{}), "model": slug,
                "case_id":cid,"gold_label":cmap[cid]["gold_label"],"category":cmap[cid]["category"]}
    for mk in list(METHODS)+list(BASELINE_SINGLE):
        rows=[rec(mk,c["id"]) for c in cases]; json.dump(rows,open(R.OUTDIR/f"{slug}__{mk}.json","w"),indent=2,ensure_ascii=False); combined[mk]=rows
    sc_rows=[]
    for c in cases:
        samples=[R._norm(R.extract_json(results_by_meta.get(("sc",c["id"],i),{}).get("text") or "").get("label")) for i in range(SC_K)]
        votes=Counter(s for s in samples if s not in ("ERROR","PARSE_ERROR"))
        top,agree=(votes.most_common(1)[0][0],votes.most_common(1)[0][1]/SC_K) if votes else ("PARSE_ERROR",0.0)
        sc_rows.append({"response":{"label":top},"sc_samples":samples,"sc_votes":dict(votes),"sc_agreement":agree,
                        "case_id":c["id"],"gold_label":c["gold_label"],"category":c["category"]})
    json.dump(sc_rows,open(R.OUTDIR/f"{slug}__sc.json","w"),indent=2,ensure_ascii=False); combined["sc"]=sc_rows
    rag_rows=[]
    for c in cases:
        row=rec("rag",c["id"]); row["rag_neighbors"]=rag_nb.get(c["id"],[]); rag_rows.append(row)
    json.dump(rag_rows,open(R.OUTDIR/f"{slug}__rag.json","w"),indent=2,ensure_ascii=False); combined["rag"]=rag_rows
    json.dump(combined,open(R.OUTDIR/f"{slug}__all.json","w"),indent=2,ensure_ascii=False)
    print(f"reconstructed {slug}: {sorted(combined.keys())}")


if __name__ == "__main__":
    models=[tuple(a.split(":")) for a in sys.argv[1:]]
    cases=json.load(open(R.DATASET))["cases"]
    embs=R._embed(R.EMBED_MODEL_DEFAULT,[c["text"] for c in cases])
    jobs=[]
    for model,slug in models:
        src,meta,rag_nb=build_for_model(cases,embs)
        job=gc.batches.create(model=model, src=src, config=types.CreateBatchJobConfig(display_name=f"florence-{slug}"))
        print(f"submitted {slug}: {job.name} ({len(src)} reqs)")
        jobs.append((model,slug,job.name,meta,rag_nb))
    for model,slug,name,meta,rag_nb in jobs:
        while True:
            j=gc.batches.get(name=name); st=str(j.state)
            print(f"  {slug}: {st}")
            if "SUCCEEDED" in st or "FAILED" in st or "CANCELLED" in st or "EXPIRED" in st: break
            time.sleep(60)
        if "SUCCEEDED" not in str(j.state):
            print(f"  {slug} did not succeed: {j.state} {getattr(j,'error',None)}"); continue
        results_by_meta={}
        for idx,ir in enumerate(j.dest.inlined_responses):
            mk,cid,i=meta[idx]
            txt=resp_text(ir.response) if ir.response else ""
            um=getattr(ir.response,"usage_metadata",None) if ir.response else None
            usage={}
            if um:
                out=(um.candidates_token_count or 0)+(getattr(um,"thoughts_token_count",0) or 0)
                usage={"prompt_tokens":um.prompt_token_count,"completion_tokens":out,"total_tokens":(um.prompt_token_count or 0)+out}
            results_by_meta[(mk,cid,i)]={"text":txt,"usage":usage}
        reconstruct(slug,cases,results_by_meta,rag_nb)

"""
Real-document experiment (R3.1/R4#2,3): run ED / Strict EC / Normalcy EC on the
un-curated natural paragraphs (dataset_realdoc.json), 6 API models across 3 vendors,
Batch API (50%). Writes results_realdoc/{slug}__{config}.json in the standard schema.
"""
import os, sys, json, time, io
os.environ.setdefault("OPENWEIGHT_PROVIDER", "openai")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_open_models as R
from prompts_core import METHODS
import openai, anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from google import genai
from google.genai import types

DS_PATH = os.environ.get("REALDOC_DS", os.path.join(os.path.dirname(HERE), "dataset", "dataset_realdoc.json"))
DS = json.load(open(DS_PATH))["cases"]
OUT = os.environ.get("REALDOC_OUT", os.path.join(HERE, "results_realdoc")); os.makedirs(OUT, exist_ok=True)
CFG = ["ed", "strict_ec", "normalcy_ec"]
MAXTOK = 4000
oc = openai.OpenAI(); ac = anthropic.Anthropic(); gc = genai.Client()

def umsg(c):
    return f"Analyze the following construction report excerpt:\n\n{c['text']}"

def rec(c, content):
    return {"response": R.extract_json(content) if content else {"parse_error": True},
            "case_id": c["id"], "gold_label": c["gold_label"], "doc_outcome": c.get("doc_outcome"),
            "source_report": c.get("source_report"), "category": c["category"]}

def save(slug, cfg, rows):
    json.dump(rows, open(f"{OUT}/{slug}__{cfg}.json", "w"), indent=2, ensure_ascii=False)
    print(f"  wrote {slug}__{cfg} ({len(rows)})")

# ---------- OpenAI (chat.completions batch) ----------
def run_openai(model, slug):
    buf = io.StringIO()
    for cfg in CFG:
        for c in DS:
            buf.write(json.dumps({"custom_id": f"{cfg}-{c['id']}", "method": "POST", "url": "/v1/chat/completions",
                "body": {"model": model, "max_completion_tokens": MAXTOK, "reasoning_effort": "high",
                         "response_format": {"type": "json_object"},
                         "messages": [{"role": "system", "content": METHODS[cfg]["prompt"]}, {"role": "user", "content": umsg(c)}]}}) + "\n")
    fobj = oc.files.create(file=("rd.jsonl", buf.getvalue().encode()), purpose="batch")
    b = oc.batches.create(input_file_id=fobj.id, endpoint="/v1/chat/completions", completion_window="24h")
    print(f"{slug}: openai batch {b.id}")
    while b.status not in ("completed", "failed", "expired", "cancelled"):
        time.sleep(60); b = oc.batches.retrieve(b.id); print(f"  {slug} {b.status} {b.request_counts}")
    res = {}
    for line in oc.files.content(b.output_file_id).text.splitlines():
        o = json.loads(line); res[o["custom_id"]] = o["response"]["body"]["choices"][0]["message"]["content"]
    for cfg in CFG:
        save(slug, cfg, [rec(c, res.get(f"{cfg}-{c['id']}")) for c in DS])

# ---------- Anthropic batch ----------
def run_claude(model, slug):
    reqs = [Request(custom_id=f"{cfg}-{c['id']}", params=MessageCreateParamsNonStreaming(
        model=model, max_tokens=MAXTOK, system=METHODS[cfg]["prompt"],
        messages=[{"role": "user", "content": umsg(c)}])) for cfg in CFG for c in DS]
    b = ac.messages.batches.create(requests=reqs); print(f"{slug}: claude batch {b.id}")
    while True:
        b = ac.messages.batches.retrieve(b.id); print(f"  {slug} {b.processing_status} {b.request_counts}")
        if b.processing_status == "ended": break
        time.sleep(60)
    res = {}
    for r in ac.messages.batches.results(b.id):
        res[r.custom_id] = ("".join(x.text for x in r.result.message.content if x.type == "text")
                            if r.result.type == "succeeded" else None)
    for cfg in CFG:
        save(slug, cfg, [rec(c, res.get(f"{cfg}-{c['id']}")) for c in DS])

# ---------- Gemini batch (one batch per config since model is batch-level) ----------
def run_gemini(model, slug):
    out = {cfg: {} for cfg in CFG}
    for cfg in CFG:
        src = [types.InlinedRequest(contents=umsg(c), metadata={"k": c["id"]},
               config=types.GenerateContentConfig(system_instruction=METHODS[cfg]["prompt"],
               response_mime_type="application/json", temperature=0)) for c in DS]
        job = gc.batches.create(model=model, src=src, config=types.CreateBatchJobConfig(display_name=f"rd-{slug}-{cfg}"))
        print(f"{slug}/{cfg}: gemini {job.name}")
        while True:
            j = gc.batches.get(name=job.name); st = str(j.state)
            if any(x in st for x in ("SUCCEEDED", "FAILED", "CANCELLED", "EXPIRED")): break
            time.sleep(60)
        rows = []
        for idx, ir in enumerate(j.dest.inlined_responses):
            txt = ""
            if ir.response:
                try: txt = ir.response.text or ""
                except Exception: txt = ""
            rows.append(rec(DS[idx], txt))
        save(slug, cfg, rows)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = {
        "gpt_5_4_mini": ("openai", "gpt-5.4-mini"), "gpt_5_5": ("openai", "gpt-5.5"),
        "claude_opus_4_8": ("claude", "claude-opus-4-8"), "claude_sonnet_4_6": ("claude", "claude-sonnet-4-6"),
        "gemini_3_5_flash": ("gemini", "gemini-3.5-flash"), "gemini_3_1_pro": ("gemini", "gemini-3.1-pro-preview"),
    }
    fns = {"openai": run_openai, "claude": run_claude, "gemini": run_gemini}
    for slug, (vendor, model) in jobs.items():
        if target not in ("all", vendor, slug): continue
        try:
            fns[vendor](model, slug)
        except Exception as e:
            print(f"!! {slug} failed: {e}")
    print("DONE", target)

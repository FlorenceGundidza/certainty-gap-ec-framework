"""
R4#12: independent multi-annotator validation of the failure taxonomy.
Three independent LLM annotators (distinct vendors) re-label the 23 failure cases
with the SAME 6-category taxonomy; report Fleiss' kappa + agreement with the
original gpt-5.4-mini diagnosis. Sync calls (69 total, cheap).
"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# load OPENAI key from florence/.env; ANTHROPIC/GOOGLE from env (eval'd in shell)
for line in open(os.path.join(ROOT, ".env")):
    if line.startswith("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()

from experiment_v5_anatomy import DIAGNOSTIC_PROMPT
import openai, anthropic
from google import genai
from google.genai import types

CATS = ["Temporal & Modality Confusion", "Scope & Granularity Mismatch", "Recovery Neglect",
        "Lexical Overheating", "Scope-Change Conflation", "Excessive Conservatism (Over-Abstention)"]


def norm_cat(s):
    if not s:
        return None
    s = re.sub(r"^\s*\d+[\.\)]\s*", "", str(s)).strip().lower()
    for c in CATS:
        cl = c.lower()
        if s == cl or s in cl or cl.split(" (")[0] in s:
            return c
    if "temporal" in s or "modality" in s:
        return CATS[0]
    if "granularity" in s or ("scope" in s and "change" not in s and "conflation" not in s):
        return CATS[1]
    if "recovery" in s:
        return CATS[2]
    if "lexical" in s or "overheat" in s:
        return CATS[3]
    if "conflation" in s or "scope-change" in s:
        return CATS[4]
    if "conservat" in s or "abstention" in s:
        return CATS[5]
    return None


def extract_json(t):
    if not t:
        return {}
    st = t.find("{")
    if st < 0:
        return {}
    d = 0
    for i in range(st, len(t)):
        if t[i] == "{":
            d += 1
        elif t[i] == "}":
            d -= 1
            if d == 0:
                try:
                    return json.loads(t[st:i + 1])
                except Exception:
                    return {}
    return {}


def user_content(f):
    return (f"# Case Data\n- Input Text: {f['text']}\n- Gold Label: {f['gold']}\n"
            f"- LLM Response Label: {f['pred']}\n- LLM Response (partial): {f['response_json'][:300]}\n\nAnalyze this failure.")

oc = openai.OpenAI()
ac = anthropic.Anthropic()
gc = genai.Client()


def judge_openai(f):
    r = oc.chat.completions.create(model="gpt-5.4-mini", max_completion_tokens=2048, reasoning_effort="high",
                                   response_format={"type": "json_object"},
                                   messages=[{"role": "system", "content": DIAGNOSTIC_PROMPT}, {"role": "user", "content": user_content(f)}])
    return extract_json(r.choices[0].message.content)


def judge_claude(f):
    r = ac.messages.create(model="claude-sonnet-4-6", max_tokens=2048, system=DIAGNOSTIC_PROMPT,
                           messages=[{"role": "user", "content": user_content(f)}])
    return extract_json("".join(b.text for b in r.content if b.type == "text"))


def judge_gemini(f):
    r = gc.models.generate_content(model="gemini-3.5-flash", contents=user_content(f),
                                   config=types.GenerateContentConfig(system_instruction=DIAGNOSTIC_PROMPT, response_mime_type="application/json", temperature=0))
    return extract_json(r.text or "")


JUDGES = {"gpt-5.4-mini": judge_openai, "claude-sonnet-4-6": judge_claude, "gemini-3.5-flash": judge_gemini}


def fleiss_kappa(rows):  # rows: list of dicts cat->count, n raters each
    N = len(rows)
    n = sum(rows[0].values())
    cats = CATS
    P_i = []
    for r in rows:
        s = sum(r.get(c, 0) ** 2 for c in cats)
        P_i.append((s - n) / (n * (n - 1)))
    P_bar = sum(P_i) / N
    p_j = {c: sum(r.get(c, 0) for r in rows) / (N * n) for c in cats}
    P_e = sum(v ** 2 for v in p_j.values())
    return (P_bar - P_e) / (1 - P_e) if (1 - P_e) else float("nan"), P_bar, P_e


if __name__ == "__main__":
    failures = json.load(open(os.path.join(HERE, "failure_cases_all.json")))
    orig = {d["case_id"]: norm_cat(d.get("diagnosis", {}).get("primary_failure_category"))
            for d in json.load(open(os.path.join(HERE, "results_v5_anatomy/all_diagnoses.json")))}
    out = []
    for f in failures:
        labels = {}
        for name, fn in JUDGES.items():
            try:
                labels[name] = norm_cat(fn(f).get("primary_failure_category"))
            except Exception as e:
                labels[name] = None
                print(f"  {f['case_id']} {name} ERR {e}")
        out.append({"case_id": f["case_id"], "gold": f["gold"], "pred": f["pred"], "labels": labels})
        print(f"{f['case_id']}: {[labels[j] for j in JUDGES]}")
    json.dump(out, open(os.path.join(HERE, "reannotation_3judges.json"), "w"), indent=2, ensure_ascii=False)

    valid = [o for o in out if all(o["labels"][j] for j in JUDGES)]
    from collections import Counter
    rows = [dict(Counter(o["labels"][j] for j in JUDGES)) for o in valid]
    kappa, Pbar, Pe = fleiss_kappa(rows)
    unanimous = sum(1 for o in valid if len(set(o["labels"][j] for j in JUDGES)) == 1)
    majority = sum(1 for o in valid if max(Counter(o["labels"][j] for j in JUDGES).values()) >= 2)
    # agreement of judge-majority with original diagnosis
    agree_orig = 0
    for o in valid:
        c = Counter(o["labels"][j] for j in JUDGES); mj = c.most_common(1)[0][0]
        if orig.get(o["case_id"]) == mj:
            agree_orig += 1
    print("\n=== R4#12 independent re-annotation ===")
    print(f"items with 3 valid labels: {len(valid)}/{len(out)}")
    print(f"Fleiss kappa (3 judges, 6 cats): {kappa:.3f}  (P_bar={Pbar:.3f}, P_e={Pe:.3f})")
    print(f"unanimous (3/3): {unanimous}/{len(valid)} ({unanimous/len(valid)*100:.0f}%)")
    print(f"majority (>=2/3): {majority}/{len(valid)} ({majority/len(valid)*100:.0f}%)")
    print(f"judge-majority == original gpt-5.4-mini diagnosis: {agree_orig}/{len(valid)} ({agree_orig/len(valid)*100:.0f}%)")

import json
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
import platform
from PIL import Image

# -----------------------------
# helper: open image file
# -----------------------------
def open_image(file_path):
    system = platform.system()

    try:
        img = Image.open(file_path)
        img.show()
        return
    except Exception:
        pass

    # fallback OS-specific
    if system == "Windows":
        os.startfile(file_path)
    elif system == "Darwin":  # macOS
        os.system(f"open '{file_path}'")
    else:  # Linux
        os.system(f"xdg-open '{file_path}'")

client = OpenAI()

# -----------------------------
# 1. Load model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 2. Load rules (CSV)
# -----------------------------
def load_rules(csv_path="rules.csv"):
    return pd.read_csv(csv_path)

rules_df = load_rules("rules.csv")

# def build_rules_text(df):
#     return "\n".join(
#         f"{r['Code']}: {r['Name']} -> {r['Message']}"
#         for _, r in df.iterrows()
#     )

# RULES_TEXT = build_rules_text(rules_df)

def build_rules_text(df):
    return "\n".join(
        f"- {row['Malpractice']}"
        for _, row in df.iterrows()
    )

RULES_TEXT = build_rules_text(rules_df)

# -----------------------------
# 3. Load memes
# -----------------------------
def load_memes(path="memes.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

memes = load_memes("memes.json")

# -----------------------------
# 4. Build meme text (IMPORTANT: include tags)
# -----------------------------
def build_text(meme):
    return (
        meme.get("description", "") + " " +
        " ".join(meme.get("intent", [])) + " " +
        " ".join(meme.get("tone", [])) + " " +
        " ".join(meme.get("structure", []))
    )

meme_names = list(memes.keys())
meme_texts = [build_text(memes[m]) for m in meme_names]

# -----------------------------
# 5. Encode + FAISS
# -----------------------------
def encode(texts):
    return np.array(model.encode(texts, normalize_embeddings=True))

embeddings = encode(meme_texts)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# -----------------------------
# 6. Analyze code with rules + humor constraint
# -----------------------------
def analyze_code(code_text):
    prompt = f"""
You are a static code analysis assistant. Be short and compact.

RULE DATABASE:
{RULES_TEXT}

CODE:
{code_text}

Return:
- only one issue, the one that seems more critical
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise static code analysis engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    # print("analisis of code: ", response.choices[0].message.content, end="\n\n\n")
    return response.choices[0].message.content

# -----------------------------
# 7. Meme search WITH TAG FILTERING
# -----------------------------
def search_memes(query, user_tags, k=5):
    q_emb = encode([query])
    scores, indices = index.search(q_emb, k * 3)  # oversample

    user_tags = set(t.strip().lower() for t in user_tags.split(","))

    results = []

    for i, score in zip(indices[0], scores[0]):
        name = meme_names[i]
        meme = memes[name]

        meme_tags = set(
            (meme.get("intent", []) +
             meme.get("tone", []) +
             meme.get("structure", []))
        )

        meme_tags = set(t.lower() for t in meme_tags)

        # TAG COMPATIBILITY SCORE (simple intersection)
        tag_overlap = len(user_tags & meme_tags)

        results.append({
            "name": name,
            "score": float(score),
            "tag_score": tag_overlap,
            "meme": meme
        })

    # rerank: semantic + tag alignment
    results.sort(key=lambda x: (x["tag_score"], x["score"]), reverse=True)

    return results[:k]

# -----------------------------
# 8. LLM explanation (TAG-AWARE)
# -----------------------------
def explain_meme(code_analysis, meme, user_tags):
    prompt = f"""
You are a meme generator for debugging humor.

You must respect the user's humor style:
USER TAGS: {user_tags}

TASK:
- Adapt tone to user tags
- Write a caption matching the humor style, be explicit about the error relation and be short

---

CODE ANALYSIS:
{code_analysis}

---

MEME:
Name: {meme["name"]}
Description: {meme["meme"].get("description")}
Intent: {meme["meme"].get("intent")}
Tone: {meme["meme"].get("tone")}
Structure: {meme["meme"].get("structure")}

---

Return:
CAPTION:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You adapt meme humor style strictly to user preferences."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content

# -----------------------------
# 9. FULL PIPELINE
# -----------------------------
def meme_pipeline(code_text, user_tags):
    # 1. analyze code
    analysis = analyze_code(code_text)

    # 2. retrieve meme
    memes_ranked = search_memes(analysis, user_tags, k=5)
    import random
    random.shuffle(memes_ranked)
    # print(memes_ranked)
    best = memes_ranked[0]

    # 3. explain + caption
    explanation = explain_meme(analysis, best, user_tags)

    # 4. OPEN IMAGE FILE
    meme_filename = best["name"]

    # adjust this folder to your dataset location
    meme_path = os.path.join("memes", meme_filename)

    open_image(meme_path)

    return {
        "analysis": analysis,
        "selected_meme": best["name"],
        "score": best["score"],
        "tag_score": best["tag_score"],
        "meme_metadata": best["meme"],
        "explanation": explanation
    }
# -----------------------------
# 10. Example
# -----------------------------
if __name__ == "__main__":

    # tags and codefile as input##########
    tags = "educational, funny"
    codefile = "SmellyUnannotated/helper_code.py"

    with open(codefile, "r", encoding="utf-8") as f:
        code = f.read()
        
        result = meme_pipeline(code, tags)

    print("\n=== ANALYSIS ===\n")
    print(result["analysis"])

    print("\n=== MEME ===\n")
    print(result["selected_meme"])

    print("\n=== EXPLANATION ===\n")
    print(result["explanation"])
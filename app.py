from flask import Flask, render_template_string, request
import json
import math
import re
import os
import requests

app = Flask(__name__)

# 🔹 Load data
with open("inverted_index.json", "r") as f:
    inverted_index = json.load(f)

with open("processed_docs.json", "r") as f:
    processed_docs = json.load(f)

with open("documents.json", "r") as f:
    documents = json.load(f)

with open("graph.json", "r") as f:
    graph = json.load(f)

TOTAL_DOCS = len(processed_docs)

# 🔥 PageRank
def compute_pagerank(graph, iterations=10, d=0.85):
    N = len(graph)
    ranks = {doc: 1/N for doc in graph}

    for _ in range(iterations):
        new_ranks = {}
        for page in graph:
            rank_sum = 0
            for other_page in graph:
                if page in graph[other_page] and len(graph[other_page]) > 0:
                    rank_sum += ranks[other_page] / len(graph[other_page])
            new_ranks[page] = (1-d)/N + d * rank_sum
        ranks = new_ranks

    return ranks

pagerank = compute_pagerank(graph)

# 🔥 Highlight words in preview
def highlight_text(text, words):
    def repl(match):
        return f"<span class='hl'>{match.group(0)}</span>"

    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(repl, text)

    return text

# 🔥 Better snippet (center around first match)
def make_snippet(text, words, window=120):
    text_lower = text.lower()
    idx = -1

    for w in words:
        idx = text_lower.find(w)
        if idx != -1:
            break

    if idx == -1:
        return text[:200]

    start = max(0, idx - window//2)
    end = min(len(text), idx + window//2)
    snippet = text[start:end]

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet

# 🔥 SEARCH FUNCTION
def search(query):
    query = query.lower().strip()
    words = query.split()

    if not words:
        return [],[]

    result_docs = None

    # AND logic
    for word in words:
        if word in inverted_index:
            docs = set(inverted_index[word])
            if result_docs is None:
                result_docs = docs
            else:
                result_docs = result_docs.intersection(docs)
        else:
            return [],[]

    scores = {}

    for doc_id in result_docs:
        score = 0
        for word in words:
            tf = processed_docs[doc_id].count(word)
            df = len(inverted_index[word])
            idf = math.log(TOTAL_DOCS / (1 + df))
            score += tf * idf

        score += pagerank.get(doc_id, 0)
        scores[doc_id] = score

    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_docs, words

# 🔥 MODERN HTML UI
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini Search Engine</title>
    <style>
        body { font-family: Arial; background: #0f172a; color: #e5e7eb; margin:0; }
        .container { width: 60%; margin: auto; padding-top: 60px; }
        h1 { text-align: center; }
        form { display:flex; gap:10px; justify-content:center; margin:30px 0; }
        input { width: 70%; padding: 12px; font-size: 18px; border-radius: 8px; border:none; }
        button { padding: 12px 20px; font-size: 16px; border:none; border-radius:8px; background:#3b82f6; color:white; cursor:pointer; }
        .result { background:#1e293b; padding:15px; margin-bottom:15px; border-radius:10px; }
        .score { color:#93c5fd; font-size:14px; }
        .hl { background: yellow; color:black; font-weight:bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Mini Search Engine</h1>

        <form method="POST">
            <input type="text" name="query" placeholder="Search anything..." required />
            <button type="submit">Search</button>
        </form>

        {% for doc_id, score, preview in results %}
        <div class="result">
            <div class="score">Doc {{doc_id}} | Score: {{score}}</div>
            <p>{{preview | safe}}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    results_data = []

    if request.method == "POST":
        query = request.form["query"]
        results, words = search(query)
        print("DEBUG RESULTS:", results)

        for doc_id, score in results:
            raw_text = documents[doc_id]
            snippet = make_snippet(raw_text, words)
            highlighted = highlight_text(snippet, words)

            results_data.append((doc_id, round(score,3), highlighted))

    return render_template_string(HTML, results=results_data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

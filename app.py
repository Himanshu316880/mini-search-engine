from flask import Flask, render_template_string, request
import json
import math
import re
import os
import requests

API_KEY = "8ef87420e35cc196ce1716b032e75240df5999c654b637c3a8a9b507ff2c3f71"

app = Flask(__name__)

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return text.lower()

with open("inverted_index.json", "r") as f:
    inverted_index = json.load(f)

with open("processed_docs.json", "r") as f:
    processed_docs = json.load(f)

with open("documents.json", "r") as f:
    documents = json.load(f)

with open("graph.json", "r") as f:
    graph = json.load(f)

TOTAL_DOCS = len(processed_docs)

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

def search_local(query):
    query = clean_text(query)
    words = query.split()

    if not words:
        return [], []

    result_docs = None

    for word in words:
        if word in inverted_index:
            docs = set(inverted_index[word])
            if result_docs is None:
                result_docs = docs
            else:
                result_docs = result_docs.intersection(docs)
        else:
            return [], []

    scores = {}

    for doc_id in result_docs:
        doc_id = str(doc_id)
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

def search_google(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": API_KEY,
        "engine": "google"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    videos = []

    if "organic_results" in data:
        for r in data["organic_results"][:5]:
            results.append({
                "title": r.get("title"),
                "link": r.get("link"),
                "snippet": r.get("snippet")
            })

    if "video_results" in data:
        for v in data["video_results"][:3]:
            videos.append(v.get("link"))

    return results, videos

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Mini Google</title>
<style>
body { font-family: Arial; background: #fff; }
.container { width: 60%; margin: auto; margin-top: 80px; }
h1 { text-align: center; font-size: 48px; color: #4285F4; }
form { display: flex; justify-content: center; margin: 30px 0; }

input {
    width: 60%;
    padding: 14px;
    font-size: 18px;
    border-radius: 30px;
    border: 1px solid #ccc;
}

button {
    margin-left: 10px;
    padding: 12px 20px;
    border-radius: 25px;
    border: none;
    background: #4285F4;
    color: white;
}

.result { margin: 20px 0; }

.title {
    color: #1a0dab;
    font-size: 20px;
    text-decoration: none;
}

.snippet {
    color: #4d5156;
    font-size: 14px;
}

.video { margin-top: 40px; }
</style>
</head>

<body>

<div class="container">
    <h1>Google Lite</h1>

    <form method="POST">
        <input type="text" name="query" placeholder="Search anything..." required>
        <button type="submit">Search</button>
    </form>

    {% for r in google_results %}
        <div class="result">
            <a class="title" href="{{r.link}}" target="_blank">{{r.title}}</a>
            <div class="snippet">{{r.snippet}}</div>
        </div>
    {% endfor %}

    {% for doc_id, score, preview in local_results %}
        <div class="result">
            <div class="title">Local Result {{doc_id}}</div>
            <div class="snippet">{{preview | safe}}</div>
        </div>
    {% endfor %}

    {% if videos %}
    <div class="video">
        <h2>Videos</h2>
        {% for v in videos %}
            <iframe width="300" height="170" src="{{v}}"></iframe>
        {% endfor %}
    </div>
    {% endif %}

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    google_results = []
    local_results = []
    videos = []

    if request.method == "POST":
        query = request.form["query"]

        google_results, videos = search_google(query)

        results, words = search_local(query)

        for doc_id, score in results:
            raw_text = documents[str(doc_id)]
            snippet = raw_text[:200]
            local_results.append((doc_id, round(score, 3), snippet))

    return render_template_string(
        HTML,
        google_results=google_results,
        local_results=local_results,
        videos=videos
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
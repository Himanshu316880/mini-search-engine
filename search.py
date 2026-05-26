import json
import os
import math

# 🔹 Check files
for file in ["inverted_index.json", "processed_docs.json", "documents.json", "graph.json"]:
    if not os.path.exists(file):
        print(f"Missing {file}")
        exit()

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

# 🔥 STEP 1: CALCULATE PAGERANK
def compute_pagerank(graph, iterations=10, d=0.85):
    N = len(graph)

    # Initial rank
    ranks = {doc: 1/N for doc in graph}

    for _ in range(iterations):
        new_ranks = {}

        for page in graph:
            rank_sum = 0

            for other_page in graph:
                if page in graph[other_page]:
                    rank_sum += ranks[other_page] / len(graph[other_page])

            new_ranks[page] = (1 - d)/N + d * rank_sum

        ranks = new_ranks

    return ranks

pagerank = compute_pagerank(graph)

# 🔥 SEARCH FUNCTION
def search(query):
    query = query.lower()
    words = query.split()

    if not words:
        return []

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
            return []

    scores = {}

    for doc_id in result_docs:
        score = 0

        for word in words:
            tf = processed_docs[doc_id].count(word)
            df = len(inverted_index[word])
            idf = math.log(TOTAL_DOCS / (1 + df))

            score += tf * idf

        # 🔥 ADD PAGERANK
        score += pagerank.get(doc_id, 0)

        scores[doc_id] = score

    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_docs


# 🔹 MAIN LOOP
while True:
    query = input("\nEnter search query (or 'exit'): ")

    if query == "exit":
        break

    results = search(query)

    if not results:
        print("No results ❌")
    else:
        for doc_id, score in results:
            print("\n----------------------")
            print(f"Doc {doc_id} | Score: {round(score,3)}")
            print(documents[doc_id][:200])
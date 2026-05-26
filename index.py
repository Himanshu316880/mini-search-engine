import json

# Load processed documents
with open("processed_docs.json", "r", encoding="utf-8") as f:
    processed_docs = json.load(f)

# Inverted index
inverted_index = {}

# Build index
for doc_id, words in processed_docs.items():

    for word in words:

        if word not in inverted_index:
            inverted_index[word] = []

        if doc_id not in inverted_index[word]:
            inverted_index[word].append(doc_id)

# Save index
with open("inverted_index.json", "w", encoding="utf-8") as f:
    json.dump(inverted_index, f, indent=2)

print("Inverted Index created successfully!")
print("Total unique words:", len(inverted_index))
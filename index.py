import json
import re

# 🔹 Load RAW documents (IMPORTANT CHANGE)
with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

# 🔹 Stopwords
stopwords = {
    "the", "is", "in", "and", "to", "of", "a", "it", "for", "on", "with"
}

# 🔹 Clean function
def clean_text(text):
    text = re.sub(r'<.*?>', '', text)  # remove HTML
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)  # remove symbols
    text = text.lower()
    return text

# 🔹 STEP 1: PROCESS DOCUMENTS
processed_docs = {}

for doc_id, text in documents.items():
    clean = clean_text(text)
    words = clean.split()

    clean_words = []
    for word in words:
        if word not in stopwords:
            clean_words.append(word)

    processed_docs[doc_id] = clean_words

# 🔹 Save processed docs
with open("processed_docs.json", "w", encoding="utf-8") as f:
    json.dump(processed_docs, f, indent=2)

print("✅ Processed docs created")

# 🔹 STEP 2: CREATE INVERTED INDEX
inverted_index = {}

for doc_id, words in processed_docs.items():
    for word in words:
        if word not in inverted_index:
            inverted_index[word] = []
        if doc_id not in inverted_index[word]:
            inverted_index[word].append(doc_id)

# 🔹 Save inverted index
with open("inverted_index.json", "w", encoding="utf-8") as f:
    json.dump(inverted_index, f, indent=2)

print("✅ Inverted index created")
print("Total unique words:", len(inverted_index))
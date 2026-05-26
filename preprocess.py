import json
import re

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

stopwords = {
    "the", "is", "in", "and", "to", "of", "a", "it", "for", "on", "with"
}

processed_docs = {}

for doc_id, text in documents.items():

    text = text.lower()

    text = re.sub(r'[^a-z0-9\s]', '', text)

    clean = clean_text(text)  
    words = clean.split()     

    clean_words = []
    for word in words:
        if word not in stopwords:
            clean_words.append(word)

    processed_docs[doc_id] = clean_words

with open("processed_docs.json", "w", encoding="utf-8") as f:
    json.dump(processed_docs, f, indent=2)

print("Preprocessing completed!")
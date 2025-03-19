from flask import Flask, request, jsonify
from flask_cors import CORS
import cohere
import os
import pdfplumber
import numpy as np
import json
from rouge import Rouge
from bert_score import score as bert_score

app = Flask(__name__)
CORS(app)

# 🔹 Initialize Cohere API
COHERE_API_KEY = "0GEryQyc5ClDVhIH8LaljPrZcI2NCaf4AaIlzNld"  # Replace with actual API key
cohere_client = cohere.Client(COHERE_API_KEY)

# 🔹 FAQs File
FAQ_FILE = "chatbot-backend/faqs.json"

def load_faqs():
    """Dynamically reload FAQs from file before every request."""
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("faq", [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Warning: FAQs file not found or corrupted. Creating new one.")
        return []

# 🔹 Directory containing PDFs
PDF_FOLDER = "chatbot-backend/pdfs"
documents = []

def extract_text_from_pdfs(pdf_folder):
    """Extract and merge text from all PDFs into a single document."""
    global documents
    documents = []

    if not os.path.exists(pdf_folder):
        print(f"❌ Folder '{pdf_folder}' does not exist.")
        return

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("⚠️ No PDFs found.")
        return

    combined_text = ""
    for pdf in pdf_files:
        with pdfplumber.open(os.path.join(pdf_folder, pdf)) as pdf_reader:
            text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
            combined_text += text + "\n"

    documents.append({"text": combined_text, "source": "All PDFs combined"})
    print(f"✅ Extracted and merged text from {len(pdf_files)} PDFs.")

@app.route("/chat", methods=["POST"])
def chat():
    """Main chatbot endpoint."""
    faqs = load_faqs()  # 🔄 Reload FAQs before checking

    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    # 🔹 Check FAQ first
    for faq in faqs:
        if query.lower() == faq["question"].lower():
            print(f"✅ FAQ Match: {faq['answer']}")
            return jsonify({"response": faq["answer"]})

    # 🔹 Retrieve relevant information from PDFs
    retrieved_context = retrieve_from_cohere(query)

    # 🔹 Generate response using Cohere
    response = generate_cohere_response(query, retrieved_context)

    # 🔹 Summarize response if needed
    summarized_response = summarize_response(response)

    # 🔹 Append new Q&A pair to FAQs if valid
    if validate_answer(query, summarized_response):
        add_to_faq(query, summarized_response)

    # 🔹 Evaluate response quality
    evaluation_metrics = evaluate_response(query, summarized_response)

    print("💬 Sending response to frontend:", summarized_response)
    return jsonify({
        "response": summarized_response,
        "evaluation": evaluation_metrics
    })

def retrieve_from_cohere(query):
    """Retrieve information by embedding query against all PDF text combined."""
    if not documents:
        print("❌ No documents loaded.")
        return "No relevant data found."

    try:
        query_embed = cohere_client.embed(
            texts=[query], model="embed-english-v3.0", input_type="search_query"
        ).embeddings[0]

        doc_embed = cohere_client.embed(
            texts=[documents[0]["text"]], model="embed-english-v3.0", input_type="search_document"
        ).embeddings[0]

        # Compute similarity score
        similarity_score = cosine_similarity(query_embed, doc_embed)
        print(f"🔍 Similarity Score: {similarity_score:.4f}")

        return documents[0]["text"] if similarity_score > 0.3 else "No relevant data found."

    except Exception as e:
        print(f"❌ Cohere Retrieval API error: {e}")
        return "Error retrieving documents."

def generate_cohere_response(query, context):
    """Generate a response using Cohere's model based on full context."""
    try:
        response = cohere_client.chat(
            model="command-r",
            message=f"Context: {context}\nQuestion: {query}",
            temperature=0.3,
            max_tokens=512
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ Cohere API error: {e}")
        return "Error generating response."

def summarize_response(text):
    """Summarize long responses using Cohere's summarization model."""
    if len(text.split()) < 50:
        return text

    try:
        summary = cohere_client.summarize(
            text=text, model="command", temperature=0.3, length="medium"
        )
        return summary.summary.strip()
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return text  # Fallback to original response

def validate_answer(question, answer):
    """Validate if the generated answer is relevant before adding to FAQs."""
    faqs = load_faqs()
    rouge = Rouge()
    scores = [rouge.get_scores(answer, faq["answer"])[0]["rouge-l"]["f"] for faq in faqs]

    best_match_score = max(scores) if scores else 0
    print(f"🔎 Validation Score: {best_match_score:.4f}")
    
    return best_match_score < 0.3  # Add only if it's a new/unique answer

def add_to_faq(question, answer):
    """Append new Q&A pair to faqs.json if it's a new query and reload FAQs."""
    faqs = load_faqs()

    # Check if the question already exists
    if any(faq["question"].lower() == question.lower() for faq in faqs):
        print("🔹 Question already exists in FAQ. Skipping insertion.")
        return

    # Append new question-answer pair
    new_faq = {"question": question, "answer": answer}
    faqs.append(new_faq)
    
    # Save to file
    with open(FAQ_FILE, "w", encoding="utf-8") as f:
        json.dump({"faq": faqs}, f, indent=4)

    print(f"✅ New FAQ added: {question}")

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def evaluate_response(query, response):
    """Evaluate response quality using multiple NLP metrics."""
    faqs = load_faqs()
    rouge = Rouge()
    faq_answers = [faq["answer"] for faq in faqs]

    # Find best matching answer in FAQs
    best_match = max(faq_answers, key=lambda ans: rouge.get_scores(response, ans)[0]["rouge-l"]["f"], default="")

    # Compute ROUGE score
    rouge_scores = rouge.get_scores(response, best_match)[0] if best_match else {}

    # Compute BERTScore
    _, _, bert_f1 = bert_score([response], [best_match], lang="en", rescale_with_baseline=True)

    compression_ratio = round(len(query.split()) / len(response.split()), 2) if len(response.split()) else 0

    print("\n📊 Evaluation Metrics:")
    print(f"   - ROUGE-1: {rouge_scores.get('rouge-1', {}).get('f', 0):.4f}")
    print(f"   - ROUGE-2: {rouge_scores.get('rouge-2', {}).get('f', 0):.4f}")
    print(f"   - ROUGE-L: {rouge_scores.get('rouge-l', {}).get('f', 0):.4f}")
    print(f"   - BERTScore: {round(bert_f1.mean().item(), 4):.4f}")
    print(f"   - Compression Ratio: {compression_ratio:.4f}")

    return {
        "rouge-l": rouge_scores.get("rouge-l", {}).get("f", 0),
        "bert-score": round(bert_f1.mean().item(), 4),
        "compression_ratio": compression_ratio
    }

if __name__ == "__main__":
    extract_text_from_pdfs(PDF_FOLDER)
    app.run(host="0.0.0.0", port=5001, debug=True)

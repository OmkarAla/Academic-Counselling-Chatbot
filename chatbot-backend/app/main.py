from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import PyPDF2
import os
from sentence_transformers import SentenceTransformer
from transformers import pipeline

app = FastAPI()

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load lightweight BERT model for text generation
bert_pipeline = pipeline("text2text-generation", model="t5-small")

# Initialize FAISS index
dimension = 384  # Dimension of embeddings from MiniLM
index = faiss.IndexFlatL2(dimension)

documents = []  # List to store text chunks

# Function to process PDFs and add to FAISS index
def load_pdfs_to_faiss(pdf_folder):
    global documents
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        documents.append(text)
    embeddings = embedding_model.encode(documents)
    index.add(embeddings)

# Load PDFs into FAISS (Assuming they are in a 'pdfs' folder)
load_pdfs_to_faiss("../pdfs")  # Adjusted path since main.py is inside 'app/'

class QueryRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(query: QueryRequest):
    query_embedding = embedding_model.encode([query.message])
    _, indices = index.search(query_embedding, k=3)  # Retrieve top 3 relevant chunks
    retrieved_texts = " ".join([documents[i] for i in indices[0]])
    
    # Use lightweight BERT model for answer generation
    generated_response = bert_pipeline(f"answer: {retrieved_texts} question: {query.message}")[0]['generated_text']
    
    return {"reply": generated_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

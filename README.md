# Academic Counselling Chatbot  

This is an **AI-powered chatbot** designed for **Amrita Vishwa Vidyapeetham, Chennai Campus** to assist students with academic counselling. It provides **real-time responses** based on FAQs and dynamically retrieves relevant information from PDFs using **Retrieval-Augmented Generation (RAG)**.  

## Features  
**Dynamic FAQ Matching** - Uses **Sentence Transformers** (`Xenova/all-MiniLM-L6-v2`) to match questions with stored FAQs.  
**RAG-based Retrieval** - Extracts and processes text from **multiple PDFs** to answer questions beyond FAQs.  
**Cohere AI Integration** - Embeds text and generates responses via **Cohere's `command-r` model**.  
**Auto FAQ Expansion** - Dynamically appends new Q&A pairs if no existing match is found.  
**Multi-Metric Evaluation** - Uses **ROUGE-L, BERTScore, and Compression Ratio** to assess responses.  
**Interactive Chat UI** - Built using **React.js** with local storage support.  

---

## Project Structure  

```bash
Academic-Counselling-Chatbot
├── backend
│   ├── server.js         # Handles FAQ-based chatbot responses
│   ├── rag_backend.py    # Manages PDF-based retrieval and response generation
│   ├── faqs.json         # Stores dynamically updated FAQ pairs
│   ├── pdfs/             # Directory for uploaded academic documents
├── frontend
│   ├── src/
│   │   ├── Chatbot.js    # React-based chatbot UI
│   │   ├── index.css     # Styling for chat interface
│   ├── package.json      # Dependencies for frontend
│   ├── App.js            # Main application file
├── README.md             # Project documentation
└── .gitignore            # Files to ignore in version control
```
## Tech Stack  

### Backend  
- **Node.js (Express.js)** - API for **FAQ matching** and **dynamic updates** (`server.js`)  
- **Python (Flask)** - Handles **RAG-based PDF retrieval** and **response generation** (`rag_backend.py`)  
- **Cohere API** - Used for **embedding, retrieval, and response generation**  
- **PDF Processing** - Utilizes `pdfplumber` for **extracting content from academic PDFs**  
- **Data Storage** - `faqs.json` stores **dynamic Q&A pairs**  

### Frontend  
- **React.js** - Chatbot UI (`Chatbot.js`)  
- **Bootstrap** - For styling and UI components  
- **Local Storage** - Stores chat history **persistently**  

---

## How It Works  

### **FAQ Matching**  
**User asks a question** in the chatbot interface.  
The **FAQ database (`faqs.json`) dynamically reloads** inside `server.js`.  
If a **similar question exists**, the chatbot **returns the matched answer**.  

---

### **RAG-based Retrieval (if FAQ match fails)**  
**All PDFs are combined into a single document** in `rag_backend.py`.  
The user’s **query embedding is matched** against the document embedding.  
If **relevant information is found**, a **response is generated** using **Cohere AI**.  

---

### **FAQ Expansion**  
If **no FAQ match exists**, the chatbot **generates a new response**.  
The **relevance is verified** using **cosine similarity** between the **query and response embeddings**.  
If the **similarity score is high**, the **new Q&A pair is added to `faqs.json`**.  

---

### **Response Evaluation**  
The chatbot evaluates responses using the following NLP metrics:  

**ROUGE-L** - Measures **text similarity** with existing FAQs.  
**BERTScore** - Checks **contextual similarity** to ensure **accurate responses**.  
**Compression Ratio** - Ensures **concise** and **non-redundant** responses.  

---


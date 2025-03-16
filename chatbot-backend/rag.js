require("dotenv").config();
const fs = require("fs");
const path = require("path");
const pdfParse = require("pdf-parse");
const faiss = require("faiss-node");
const { SentenceTransformer } = require("sentence-transformers");
const { Configuration, OpenAIApi } = require("openai");

const model = new SentenceTransformer("all-MiniLM-L6-v2"); // Efficient BERT Model
const openai = new OpenAIApi(new Configuration({ apiKey: process.env.OPENAI_API_KEY }));

let index;
let documents = [];

// Load FAQs from JSON
const faqs = JSON.parse(fs.readFileSync("faqs.json", "utf8"));

// Load PDFs & Build FAISS Index
async function loadDocuments() {
    console.log("Loading PDFs and indexing embeddings...");
    const pdfFiles = fs.readdirSync("./pdfs").filter(file => file.endsWith(".pdf"));

    for (const file of pdfFiles) {
        const filePath = path.join(__dirname, "pdfs", file);
        const data = await pdfParse(fs.readFileSync(filePath));
        const textChunks = data.text.split("\n\n"); // Split into paragraphs
        documents.push(...textChunks);
    }

    console.log("Generating embeddings...");
    const embeddings = await model.encode(documents);
    index = new faiss.IndexFlatL2(embeddings[0].length);
    index.add(embeddings);
    console.log("Embeddings indexed successfully!");
}

// Retrieve best-matching text using FAISS
async function retrieveRelevantText(query) {
    const queryEmbedding = await model.encode([query]);
    const D = new Float32Array(1);
    const I = new Int32Array(1);

    index.search(queryEmbedding, 1, D, I);
    return documents[I[0]] || "No relevant document found.";
}

// Generate a response using OpenAI GPT
async function generateResponse(query, retrievedText) {
    const prompt = `
    You are an academic counseling chatbot. Given the user's question and retrieved documents, generate a helpful answer.

    User Question: ${query}
    Retrieved Context: ${retrievedText}

    Answer:
    `;

    const response = await openai.createChatCompletion({
        model: "gpt-4",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.7,
    });

    return response.data.choices[0].message.content;
}

// Main RAG function
async function processQuery(query) {
    // Check FAQs first
    if (faqs[query.toLowerCase()]) {
        return faqs[query.toLowerCase()];
    }

    // Retrieve text from PDFs
    const retrievedText = await retrieveRelevantText(query);

    // Generate final response using GPT
    return await generateResponse(query, retrievedText);
}

module.exports = { loadDocuments, processQuery };

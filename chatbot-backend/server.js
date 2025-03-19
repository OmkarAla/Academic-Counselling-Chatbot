import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import fs from "fs";
import fetch from "node-fetch";
import { pipeline } from "@xenova/transformers";

const app = express();
const PORT = 5000;

app.use(cors({
    origin: ["http://localhost:3000", "https://nlpacc.vercel.app"], // Allow both local and deployed frontend
    methods: "GET,POST,OPTIONS",
    allowedHeaders: "Content-Type,Authorization",
    credentials: true
}));

app.use(bodyParser.json());

const FAQ_FILE = "faqs.json";

// ✅ Load SentenceTransformer dynamically
let embedder;
(async () => {
    embedder = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2");
    console.log("✅ Model loaded for FAQ matching.");
})();

// 🔹 Function to dynamically reload FAQs before every request
const loadFaqs = () => {
    try {
        return JSON.parse(fs.readFileSync(FAQ_FILE, "utf8")).faq || [];
    } catch (error) {
        console.error("❌ Error loading FAQs:", error);
        return [];
    }
};

// 🔹 Function to calculate cosine similarity
const cosineSimilarity = (vecA, vecB) => {
    const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
    const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
    const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
    return dotProduct / (magnitudeA * magnitudeB);
};

app.post("/chat", async (req, res) => {
    const { query } = req.body;
    if (!query.trim()) return res.status(400).json({ response: "Invalid query." });

    const faqs = loadFaqs(); // Reload FAQs dynamically before processing
    const normalizedQuery = query.toLowerCase().trim();

    // ✅ Check direct greeting
    if (["hi", "hello", "hey"].includes(normalizedQuery)) {
        return res.json({ response: "Hello! How can I assist you today? 😊" });
    }

    // ✅ Ensure embedder is ready
    if (!embedder) {
        return res.status(500).json({ response: "Model is still loading. Try again later." });
    }

    // ✅ Compute query embedding
    const queryEmbedding = (await embedder(normalizedQuery, { pooling: "mean", normalize: true })).data;

    // ✅ Find the most similar FAQ (without pre-stored embeddings)
    let bestMatch = { answer: null, score: 0 };
    console.log("\n🔍 FAQ Similarity Scores:");
    for (const faq of faqs) {
        const faqEmbedding = (await embedder(faq.question, { pooling: "mean", normalize: true })).data;
        const score = cosineSimilarity(queryEmbedding, faqEmbedding);
        console.log(`- Question: "${faq.question}" → Score: ${score.toFixed(4)}`);

        if (score > bestMatch.score) {
            bestMatch = { answer: faq.answer, score };
        }
    }

    console.log(`✅ Best match score: ${bestMatch.score.toFixed(4)}`);

    // ✅ Return matched FAQ if score > 0.5
    if (bestMatch.score > 0.7) {
        return res.json({ response: bestMatch.answer });
    }

    // ✅ Otherwise, call RAG backend for retrieval
    let botResponse = "I'm sorry, I couldn't find an answer. Could you rephrase?";
    if (bestMatch.score < 0.7) {
        try {
            const response = await fetch("http://localhost:5001/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const data = await response.json();
            botResponse = data.response || "No relevant information found.";

            console.log(`📄 RAG response: ${botResponse}`);
        } catch (error) {
            console.error("❌ Error connecting to RAG backend:", error.message);
        }
    }

    // ✅ Append new Q&A pair to FAQs only if relevant
    await addToFaq(query, botResponse, queryEmbedding);

    return res.json({ response: botResponse });
});

async function addToFaq(question, answer, queryEmbedding) {
    let faqs = loadFaqs();

    // ✅ Check if the question already exists
    if (faqs.some(faq => faq.question.toLowerCase() === question.toLowerCase())) {
        console.log("🔹 Question already exists in FAQ. Skipping insertion.");
        return;
    }

    // ✅ Compute embedding for the answer
    const answerEmbedding = (await embedder(answer, { pooling: "mean", normalize: true })).data;
    const similarityScore = cosineSimilarity(queryEmbedding, answerEmbedding);

    console.log(`🔍 Q&A Similarity Score: ${similarityScore.toFixed(4)}`);

    // ✅ Only insert if similarity > 0.5 (ensuring relevance)
    if (similarityScore > 0.5) {
        faqs.push({ question, answer });

        fs.writeFileSync(FAQ_FILE, JSON.stringify({ faq: faqs }, null, 4), "utf8");
        console.log(`✅ New FAQ added: "${question}"`);
    } else {
        console.log("❌ Retrieved answer is not relevant enough. Skipping insertion.");
    }
}

app.listen(PORT, () => {
    console.log(`✅ Node.js server running on port ${PORT}`);
});

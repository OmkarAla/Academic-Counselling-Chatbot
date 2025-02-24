import React, { useState, useEffect } from "react";
import axios from "axios";
import './index.css'

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    const savedMessages = localStorage.getItem("chatMessages");
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, []);

  const updateMessages = (newMessages) => {
    setMessages(newMessages);
    localStorage.setItem("chatMessages", JSON.stringify(newMessages));
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    const updatedMessages = [...messages, userMessage];
    updateMessages(updatedMessages);

    try {
      const response = await axios.post("http://127.0.0.1:5000/api/chat", { message: input });

      const botMessage = { sender: "bot", text: response.data.reply };
      updateMessages([...updatedMessages, botMessage]);

    } catch (error) {
      console.error("Error fetching response:", error);
    }

    setInput("");
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem("chatMessages");
  };

  return (
    <div className="container cha">
      <h2 className="text-center h">Academic Counselling Chatbot</h2>

      <div className="chat-box border rounded p-3" style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div key={index} style={{ ...styles.message, ...(msg.sender === "user" ? styles.userMessage : styles.botMessage) }}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-group mt-3">
        <input
          type="text"
          className="form-control"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="btn btn-primary" onClick={sendMessage}>Send</button>
        <button className="btn btn-danger ms-2" onClick={clearChat}>Clear Chat</button>
      </div>
    </div>
  );
}

// CSS styles
const styles = {
  chatBox: {
    height: "80vh",
    overflowY: "auto",
    background: "#f8f9fa",
    padding: "10px",
    display: "flex",
    flexDirection: "column",
  },
  message: {
    maxWidth: "70%",  // Limit message width
    padding: "10px",
    borderRadius: "10px",
    marginBottom: "8px",
    wordWrap: "break-word",
  },
  userMessage: {
    backgroundColor: "#007bff",
    color: "white",
    alignSelf: "flex-end",  // Align user messages to the right
  },
  botMessage: {
    backgroundColor: "#e9ecef",
    color: "black",
    alignSelf: "flex-start", // Align bot messages to the left
  },
};
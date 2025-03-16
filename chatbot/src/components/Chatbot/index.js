import React, { useState, useEffect } from "react";
import "./index.css";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const savedMessages = localStorage.getItem("chatMessages");
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    } else {
      const welcomeMessage = {
        sender: "bot",
        text: "Hello! I'm your Academic Counseling Assistant. Ask me anything about Amrita Chennai Campus! 😊"
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  const updateMessages = (newMessages) => {
    setMessages(newMessages);
    localStorage.setItem("chatMessages", JSON.stringify(newMessages));
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem("chatMessages");
  };

  const sendMessage = async () => {
    if (!query.trim()) return;

    const userMessage = { sender: "user", text: query };
    const updatedMessages = [...messages, userMessage];
    updateMessages(updatedMessages);
    setQuery("");

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

      const data = await response.json();
      console.log("📩 Received from backend:", data);  // Debugging line
      const botMessage = { sender: "bot", text: formatLinks(data.response) }; 


      updateMessages([...updatedMessages, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      updateMessages([...updatedMessages, { sender: "bot", text: "Error: Unable to get response." }]);
    }
  };

  const formatLinks = (text) => {
    return text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  };

  return (
    <div className="container cha">
      <h2 className="text-center h">Academic Counselling Chatbot</h2>

      <div className="chat-box border rounded p-3" style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div key={index} style={{ ...styles.message, ...(msg.sender === "user" ? styles.userMessage : styles.botMessage) }}>
            <span dangerouslySetInnerHTML={{ __html: msg.text }} />
          </div>
        ))}
      </div>

      <div className="input-group mt-3">
        <input
          type="text"
          className="form-control"
          placeholder="Ask a question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
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
    maxWidth: "70%",
    padding: "10px",
    borderRadius: "10px",
    marginBottom: "8px",
    wordWrap: "break-word",
  },
  userMessage: {
    backgroundColor: "#007bff",
    color: "white",
    alignSelf: "flex-end",
  },
  botMessage: {
    backgroundColor: "#e9ecef",
    color: "black",
    alignSelf: "flex-start",
  },
};

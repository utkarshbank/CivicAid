"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useRef, useEffect, Suspense } from "react";
import Navbar from "@/components/Navbar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const CATEGORY_META = {
  food: { icon: "🍽️", label: "Food Assistance", color: "#4CAF50" },
  housing: { icon: "🏠", label: "Housing Support", color: "#2196F3" },
  legal: { icon: "⚖️", label: "Legal Aid", color: "#9C27B0" },
  mental_health: { icon: "🧠", label: "Mental Health", color: "#00BCD4" },
  safety: { icon: "🛡️", label: "Safety & Support", color: "#F44336" },
  transportation: { icon: "🚌", label: "Transportation", color: "#FF9800" },
  immigration: { icon: "🌍", label: "Immigration Help", color: "#3F51B5" },
  women: { icon: "👩", label: "Women's Support", color: "#E91E63" },
};

function renderMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

function ChatContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const category = searchParams.get("category") || "food";
  const catMeta = CATEGORY_META[category] || CATEGORY_META.food;

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Send initial greeting
  useEffect(() => {
    sendMessage("Hi, I need help with " + (catMeta.label || "services"), true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function sendMessage(text, isInitial = false) {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    const newMessages = isInitial ? [] : [...messages, userMsg];
    if (!isInitial) setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: newMessages,
          category: category,
        }),
      });
      const data = await res.json();
      const assistantMsg = { role: "assistant", content: data.response };

      if (isInitial) {
        setMessages([userMsg, assistantMsg]);
      } else {
        setMessages((prev) => [...prev, assistantMsg]);
      }

      // If resources returned, navigate to plan page
      if (data.resources && data.resources.length > 0) {
        sessionStorage.setItem("civicaid_resources", JSON.stringify(data.resources));
        sessionStorage.setItem("civicaid_response", data.response);
        sessionStorage.setItem("civicaid_category", category);
        setTimeout(() => router.push("/plan"), 2000);
      }
    } catch (err) {
      console.error("Chat error:", err);
      const errorMsg = {
        role: "assistant",
        content: "I'm having trouble connecting to the server. Please make sure the backend is running on port 8000. You can start it with:\n\n**cd backend && uvicorn main:app --reload**",
      };
      if (isInitial) {
        setMessages([userMsg, errorMsg]);
      } else {
        setMessages((prev) => [...prev, errorMsg]);
      }
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  // Voice input using Web Speech API
  function toggleVoice() {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Voice input is not supported in this browser. Try Chrome.");
      return;
    }
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language === "es" ? "es-US" : language === "zh" ? "zh-CN" : "en-US";
    recognition.interimResults = false;
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }

  // Voice output using browser speech synthesis
  function speakText(text) {
    const clean = text.replace(/\*\*/g, "").replace(/<[^>]*>/g, "");
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = language === "es" ? "es-US" : language === "zh" ? "zh-CN" : "en-US";
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }

  return (
    <>
      <Navbar language={language} onLanguageChange={setLanguage} />
      <div className="chat-layout">
        <div className="chat-header">
          <div className="chat-header-icon" style={{ background: catMeta.color }}>
            {catMeta.icon}
          </div>
          <div className="chat-header-info">
            <h2>CivicAid — {catMeta.label}</h2>
            <p>AI assistant • Davis & Sacramento, CA</p>
          </div>
        </div>

        <div className="chat-messages">
          {messages
            .filter((m) => m.role !== "user" || messages.indexOf(m) !== 0)
            .map((msg, i) => (
              <div
                key={i}
                className={`chat-bubble ${msg.role}`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                {msg.role === "assistant" && (
                  <button
                    className="btn-icon"
                    onClick={() => speakText(msg.content)}
                    title="Read aloud"
                    style={{ marginTop: 8, fontSize: "0.85rem", padding: "4px 8px", width: "auto" }}
                  >
                    🔊 Listen
                  </button>
                )}
              </div>
            ))}
          {loading && (
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <input
              id="chat-input"
              type="text"
              placeholder="Type your answer..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              autoComplete="off"
            />
            <button
              className={`btn-icon ${isListening ? "active" : ""}`}
              onClick={toggleVoice}
              title="Voice input"
            >
              🎤
            </button>
          </div>
          <button
            className="btn-send"
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
            title="Send"
          >
            ➤
          </button>
        </div>
      </div>
    </>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div style={{ padding: "120px 24px", textAlign: "center", color: "#94a3b8" }}>Loading chat...</div>}>
      <ChatContent />
    </Suspense>
  );
}

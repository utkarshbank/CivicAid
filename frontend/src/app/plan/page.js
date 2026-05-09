"use client";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";

const CATEGORY_COLORS = {
  food: "#4CAF50", housing: "#2196F3", legal: "#9C27B0",
  mental_health: "#00BCD4", safety: "#F44336", transportation: "#FF9800",
  immigration: "#3F51B5", women: "#E91E63", disability: "#607D8B", general: "#795548",
};

export default function PlanPage() {
  const router = useRouter();
  const [resources, setResources] = useState([]);
  const [aiSummary, setAiSummary] = useState("");
  const [category, setCategory] = useState("");
  const [language, setLanguage] = useState("en");

  useEffect(() => {
    const stored = sessionStorage.getItem("civicaid_resources");
    const summary = sessionStorage.getItem("civicaid_response");
    const cat = sessionStorage.getItem("civicaid_category");
    if (stored) setResources(JSON.parse(stored));
    if (summary) setAiSummary(summary);
    if (cat) setCategory(cat);
  }, []);

  function speakText(text) {
    const clean = text.replace(/\*\*/g, "").replace(/<[^>]*>/g, "");
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = language === "es" ? "es-US" : "en-US";
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }

  function printPlan() {
    window.print();
  }

  if (resources.length === 0) {
    return (
      <>
        <Navbar language={language} onLanguageChange={setLanguage} />
        <div className="page-container" style={{ textAlign: "center", paddingTop: 160 }}>
          <h1 style={{ fontSize: "2rem", marginBottom: 16 }}>No resources yet</h1>
          <p style={{ color: "var(--text-secondary)", marginBottom: 32 }}>
            Complete the chat intake first to get personalized recommendations.
          </p>
          <button className="btn-primary" onClick={() => router.push("/categories")}>
            Get Started →
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar language={language} onLanguageChange={setLanguage} />
      <div className="plan-header">
        <h1>🎯 Your Action Plan</h1>
        <p>Personalized resources based on your needs — {resources.length} matches found</p>
      </div>

      <div className="plan-grid">
        {resources.map((r, i) => (
          <div
            key={r.id}
            className="resource-card"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <div
              className="resource-card-accent"
              style={{ background: CATEGORY_COLORS[r.category] || "var(--gradient-accent)" }}
            />
            <div className="resource-card-body">
              <h3>{r.name}</h3>
              <p className="resource-desc">{r.description}</p>

              <div className="resource-details">
                <div className="resource-detail">
                  <span className="detail-icon">📞</span>
                  <span>{r.phone}</span>
                </div>
                {r.address && (
                  <div className="resource-detail">
                    <span className="detail-icon">📍</span>
                    <span>{r.address}</span>
                  </div>
                )}
                <div className="resource-detail">
                  <span className="detail-icon">🕐</span>
                  <span>{r.hours}</span>
                </div>
                {r.eligibility && (
                  <div className="resource-detail">
                    <span className="detail-icon">✅</span>
                    <span>{r.eligibility}</span>
                  </div>
                )}
              </div>

              <div className="resource-tags">
                {r.languages?.map((lang) => (
                  <span key={lang} className="resource-tag">{lang}</span>
                ))}
                <span className="resource-tag" style={{
                  background: CATEGORY_COLORS[r.category] + "22",
                  color: CATEGORY_COLORS[r.category],
                  borderColor: CATEGORY_COLORS[r.category] + "44",
                }}>
                  {r.type}
                </span>
              </div>

              <div className="resource-actions">
                <a href={`tel:${r.phone}`} className="action-primary">
                  📞 Call Now
                </a>
                {r.website && (
                  <a href={r.website} target="_blank" rel="noopener noreferrer">
                    🌐 Website
                  </a>
                )}
                {r.address && r.address !== "Nationwide" && !r.address.includes("Confidential") && (
                  <a
                    href={`https://maps.google.com/?q=${encodeURIComponent(r.address)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    📍 Directions
                  </a>
                )}
                <button onClick={() => speakText(`${r.name}. ${r.description}. Phone: ${r.phone}. Hours: ${r.hours}`)}>
                  🔊 Read Aloud
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="plan-actions-bar">
        <button className="btn-secondary" onClick={printPlan}>
          🖨️ Print Plan
        </button>
        <button className="btn-secondary" onClick={() => router.push("/categories")}>
          ← Choose Another Category
        </button>
        <button className="btn-primary" onClick={() => {
          sessionStorage.clear();
          router.push("/categories");
        }}>
          Start Over
        </button>
      </div>
    </>
  );
}

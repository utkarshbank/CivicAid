"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Navbar from "@/components/Navbar";

export default function Home() {
  const router = useRouter();
  const [language, setLanguage] = useState("en");

  return (
    <>
      <Navbar language={language} onLanguageChange={setLanguage} />
      <section className="hero">
        <div className="hero-badge">
          ✨ AI-Powered • Multilingual • Free
        </div>
        <h1>
          Get help faster.{" "}
          <span className="gradient-text">In your language.</span>
        </h1>
        <p className="hero-subtitle">
          CivicAid connects you to food, housing, legal aid, mental health, and
          more in Davis & Sacramento — powered by AI, available in your language,
          with voice support.
        </p>
        <div className="hero-cta">
          <button className="btn-primary" onClick={() => router.push("/categories")}>
            Find Resources →
          </button>
          <button className="btn-secondary" onClick={() => router.push("/chat")}>
            💬 Talk to CivicAid
          </button>
        </div>

        <div className="features">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Matching</h3>
            <p>
              Answer a few simple questions and our AI finds the best local
              resources tailored to your situation.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3>Multilingual Support</h3>
            <p>
              Get help in English, Spanish, Chinese, Vietnamese, Tagalog, Korean,
              and Arabic — more coming soon.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎤</div>
            <h3>Voice-Enabled</h3>
            <p>
              Speak your questions and listen to answers read aloud. Powered by
              ElevenLabs for natural, clear speech.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}

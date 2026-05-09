"use client";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";

const CATEGORIES = [
  { id: "food", icon: "🍽️", label: "Food Assistance", desc: "Food banks, CalFresh, meal programs", color: "#4CAF50" },
  { id: "housing", icon: "🏠", label: "Housing Support", desc: "Shelters, rental assistance, housing programs", color: "#2196F3" },
  { id: "legal", icon: "⚖️", label: "Legal Aid", desc: "Free legal help, tenant rights, family law", color: "#9C27B0" },
  { id: "mental_health", icon: "🧠", label: "Mental Health", desc: "Counseling, crisis lines, support groups", color: "#00BCD4" },
  { id: "safety", icon: "🛡️", label: "Safety & Support", desc: "Domestic violence, crisis intervention", color: "#F44336" },
  { id: "transportation", icon: "🚌", label: "Transportation", desc: "Bus routes, paratransit, ride programs", color: "#FF9800" },
  { id: "immigration", icon: "🌍", label: "Immigration Help", desc: "Legal clinics, refugee services, DACA", color: "#3F51B5" },
  { id: "women", icon: "👩", label: "Women's Support", desc: "Women's centers, family services, shelters", color: "#E91E63" },
];

export default function CategoriesPage() {
  const router = useRouter();
  const [language, setLanguage] = useState("en");
  const [visible, setVisible] = useState(false);

  useEffect(() => { setVisible(true); }, []);

  const handleSelect = (catId) => {
    router.push(`/chat?category=${catId}`);
  };

  return (
    <>
      <Navbar language={language} onLanguageChange={setLanguage} />
      <div className="page-container">
        <div className="page-header">
          <h1>What do you need help with?</h1>
          <p>Select a category and our AI will guide you to the right resources.</p>
        </div>
        <div className="category-grid">
          {CATEGORIES.map((cat, i) => (
            <div
              key={cat.id}
              className="category-card"
              style={{
                "--card-accent": cat.color,
                animationDelay: `${i * 0.07}s`,
                opacity: visible ? 1 : 0,
                transform: visible ? "translateY(0)" : "translateY(20px)",
                transition: `all 0.4s ease ${i * 0.07}s`,
              }}
              onClick={() => handleSelect(cat.id)}
              id={`category-${cat.id}`}
            >
              <div className="category-icon">{cat.icon}</div>
              <h3>{cat.label}</h3>
              <p>{cat.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

"use client";
import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";

export default function Navbar({ language, onLanguageChange }) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <nav className="navbar">
      <div className="navbar-brand" onClick={() => router.push("/")} style={{ cursor: "pointer" }}>
        <div className="logo-icon">🏛️</div>
        <span>CivicAid</span>
      </div>
      <div className="navbar-links">
        <a
          href="/categories"
          onClick={(e) => { e.preventDefault(); router.push("/categories"); }}
          style={pathname === "/categories" ? { color: "var(--text-primary)", background: "var(--bg-card)" } : {}}
        >
          Services
        </a>
        <a
          href="/chat"
          onClick={(e) => { e.preventDefault(); router.push("/chat"); }}
          style={pathname === "/chat" ? { color: "var(--text-primary)", background: "var(--bg-card)" } : {}}
        >
          Chat
        </a>
        <select
          className="lang-select"
          value={language || "en"}
          onChange={(e) => onLanguageChange && onLanguageChange(e.target.value)}
          aria-label="Select language"
        >
          <option value="en">🇺🇸 English</option>
          <option value="es">🇲🇽 Español</option>
          <option value="zh">🇨🇳 中文</option>
          <option value="vi">🇻🇳 Tiếng Việt</option>
          <option value="tl">🇵🇭 Tagalog</option>
          <option value="ko">🇰🇷 한국어</option>
          <option value="ar">🇸🇦 العربية</option>
        </select>
        <button
          className="nav-cta"
          onClick={() => router.push("/categories")}
        >
          Get Help
        </button>
      </div>
    </nav>
  );
}

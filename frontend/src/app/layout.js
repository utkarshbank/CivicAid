import "./globals.css";

export const metadata = {
  title: "CivicAid — Find Local Social Services",
  description: "AI-powered assistant that helps people find and apply for local social services in Davis and Sacramento, CA. Multilingual, voice-enabled, and free.",
  keywords: "social services, food assistance, housing, legal aid, mental health, Davis, Sacramento, California",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

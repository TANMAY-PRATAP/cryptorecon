import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CryptoRecon V4.0 — Multi-Chain Forensic Reconnaissance & Asset Recovery Engine",
  description: "Automated multi-chain forensic reconnaissance, VASP attribution, and asset recovery engine for Cyber Crime Cells (1930 / I4C / NCRP).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-[#090d16] text-[#f8fafc] antialiased">
        {children}
      </body>
    </html>
  );
}

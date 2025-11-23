import type { Metadata } from "next";
import { Inter, Lato, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "600", "700"]
});

const lato = Lato({
  subsets: ["latin"],
  variable: "--font-lato",
  weight: ["400", "700"]
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains"
});

export const metadata: Metadata = {
  title: "MediGraph Triage",
  description: "AI-powered medical triage assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${lato.variable} ${jetbrainsMono.variable}`}>{children}</body>
    </html>
  );
}

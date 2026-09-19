import type { Metadata, Viewport } from "next";
import { Outfit, Plus_Jakarta_Sans } from "next/font/google";

import { AppShell } from "@/components/layout/AppShell";
import { BusinessProvider } from "@/lib/BusinessContext";
import { THEME_SCRIPT, ThemeProvider } from "@/lib/theme";
import "./globals.css";

// Canva Sans is not a web font, so the type direction it sets — geometric,
// rounded, warm, no serifs and nothing futuristic — is carried by these two.
// Outfit takes the display line (greeting, wordmark, numbers), Plus Jakarta
// Sans the interface, where it stays legible down to 10px.
const display = Outfit({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const sans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "A.R.I.A. — Speak. Stock. Smarter.",
  description:
    "Adaptive Retail Intelligence Assistant. Whatever your business, whatever you need — just talk to A.R.I.A.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#FCFCFA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable}`} suppressHydrationWarning>
      <head>
        {/*
          Applies the stored theme before the first paint. Without it the page
          renders in the default theme and then snaps to the chosen one.
        */}
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-dvh bg-ink-990 font-sans antialiased">
        <ThemeProvider>
          <BusinessProvider>
            <AppShell>{children}</AppShell>
          </BusinessProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

"use client";

interface BotSummary {
  totalAccounts: number;
  totalComments: number;
  botAccounts: number;
  botAccountPct: number;
  botCommentVolume: number;
  botCommentVolumePct: number;
  avgCommentsPerBot: number;
  avgCommentsPerHuman: number;
}

interface HeroSectionProps {
  botSummary: BotSummary;
  videoCount: number;
}

export default function HeroSection({
  botSummary,
  videoCount,
}: HeroSectionProps) {
  const stats = [
    {
      label: "Comments Analyzed",
      value: botSummary.totalComments.toLocaleString(),
    },
    { label: "Videos Analyzed", value: videoCount.toLocaleString() },
    {
      label: "Unique Accounts",
      value: botSummary.totalAccounts.toLocaleString(),
    },
    {
      label: "Bot Accounts Detected",
      value: botSummary.botAccounts.toLocaleString(),
      highlight: true,
    },
  ];

  return (
    <section className="relative overflow-hidden py-20 px-6">
      <div className="absolute inset-0 bg-gradient-to-b from-red-950/20 to-transparent pointer-events-none" />
      <div className="relative max-w-5xl mx-auto text-center">
        <p className="text-sm font-medium tracking-widest uppercase text-red-400 mb-4">
          Research Project
        </p>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
          Bots in Chilean Political
          <br />
          <span className="text-red-400">YouTube</span>
        </h1>
        <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto mb-12">
          An analysis of automated accounts in the comment sections of Chilean
          political news videos, inspired by the{" "}
          <a
            href="https://factcheck.lt/eng/news/youtube_botnet_march2025/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 underline underline-offset-2 hover:text-blue-300"
          >
            FactCheck LT study (March 2025)
          </a>
          .
        </p>
        <a
          href="https://github.com/Dyotson/ChileYoutubeNewsAnalyzer"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors mb-12 border border-[var(--border)] rounded-full px-5 py-2"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
          </svg>
          View source &amp; peer-review on GitHub
        </a>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s) => (
            <div key={s.label} className="stat-card text-center">
              <p
                className={`text-3xl font-bold ${s.highlight ? "text-red-400" : ""}`}
              >
                {s.value}
              </p>
              <p className="text-sm text-[var(--text-secondary)] mt-1">
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

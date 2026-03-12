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

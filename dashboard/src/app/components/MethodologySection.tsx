"use client";

const HEURISTICS = [
  {
    title: "Username Patterns",
    desc: 'Auto-generated names ("@user-abc123"), excessive digits, random strings with no real-name pattern.',
    weight: "up to +0.35",
  },
  {
    title: "Positive Astroturfing",
    desc: 'Generic praise without substance ("Excelente!", "Tiene toda la razon"), promotional spam URLs.',
    weight: "up to +0.40",
  },
  {
    title: "Negative / Attack Bots",
    desc: "Single-word political insults as entire comments, ALL CAPS rage, repetitive spam, emoji floods.",
    weight: "up to +0.40",
  },
  {
    title: "Propaganda",
    desc: "Copy-paste slogans posted by different users, unusually formal tone with no colloquialisms.",
    weight: "up to +0.30",
  },
  {
    title: "Cross-Video Behavior",
    desc: "Same user posting identical or near-identical comments across multiple videos (Jaccard similarity > 0.6).",
    weight: "up to +0.50",
  },
];

export default function MethodologySection() {
  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Methodology</h2>
        <p className="section-subtitle">
          How we collected data and detected bots
        </p>

        <div className="grid md:grid-cols-2 gap-8 mb-10">
          <div className="stat-card">
            <h3 className="text-lg font-semibold mb-3">Data Collection</h3>
            <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
              <li>
                <strong className="text-[var(--text-primary)]">Channel scanning:</strong>{" "}
                <code className="text-xs bg-[var(--bg-primary)] px-1.5 py-0.5 rounded">scrapetube</code>{" "}
                fetches all videos from Chilean news channels
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">Political filtering:</strong>{" "}
                128 curated Spanish keywords (institutions, figures, parties, topics) filter political videos
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">Comment scraping:</strong>{" "}
                <code className="text-xs bg-[var(--bg-primary)] px-1.5 py-0.5 rounded">youtube-comment-downloader</code>{" "}
                collects all comments without the YouTube API
              </li>
            </ul>
          </div>

          <div className="stat-card">
            <h3 className="text-lg font-semibold mb-3">
              Justification: FactCheck LT
            </h3>
            <p className="text-sm text-[var(--text-secondary)] mb-3">
              Our approach is inspired by the{" "}
              <a
                href="https://factcheck.lt/eng/news/youtube_botnet_march2025/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 underline underline-offset-2"
              >
                FactCheck LT study (March 2025)
              </a>
              , which analyzed 94,532 comments across 111 channels and found:
            </p>
            <ul className="space-y-1 text-sm text-[var(--text-secondary)]">
              <li>
                Bots comprised{" "}
                <strong className="text-red-400">&lt;1%</strong> of accounts
              </li>
              <li>
                But generated{" "}
                <strong className="text-red-400">11.6%</strong> of all comments
              </li>
              <li>
                Active across{" "}
                <strong className="text-red-400">38.8%</strong> of analyzed
                videos
              </li>
            </ul>
            <p className="text-sm text-[var(--text-secondary)] mt-3">
              We apply the same account-vs-volume distinction: a user is a bot
              account if <em>any</em> of their comments score above 0.5, then{" "}
              <em>all</em> their comments count as bot-generated.
            </p>
          </div>
        </div>

        <h3 className="text-lg font-semibold mb-4">
          Bot Detection Heuristics
        </h3>
        <p className="text-sm text-[var(--text-secondary)] mb-4">
          Each comment is scored 0.0 to 1.0. Scores above{" "}
          <strong className="text-[var(--text-primary)]">0.5</strong> flag
          the comment as bot-generated. Signals stack additively, capped at 1.0.
        </p>
        <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-3">
          {HEURISTICS.map((h) => (
            <div key={h.title} className="stat-card">
              <p className="font-semibold text-sm mb-1">{h.title}</p>
              <p className="text-xs text-[var(--text-secondary)] mb-2">
                {h.desc}
              </p>
              <span className="text-xs font-mono text-yellow-400">
                {h.weight}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

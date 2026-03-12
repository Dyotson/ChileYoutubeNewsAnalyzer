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

interface ConclusionsSectionProps {
  botSummary: BotSummary;
}

export default function ConclusionsSection({
  botSummary,
}: ConclusionsSectionProps) {
  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Conclusions</h2>
        <p className="section-subtitle">Summary of findings and limitations</p>

        <div className="grid md:grid-cols-2 gap-6 mb-10">
          <div className="stat-card">
            <h3 className="text-lg font-semibold mb-4 text-red-400">
              Key Findings
            </h3>
            <ul className="space-y-3 text-sm text-[var(--text-secondary)]">
              <li>
                <strong className="text-[var(--text-primary)]">
                  {botSummary.botAccountPct}% of accounts generate{" "}
                  {botSummary.botCommentVolumePct}% of comments.
                </strong>{" "}
                This is consistent with the FactCheck LT study (&lt;1% of
                accounts, 11.6% of comments), confirming that bot activity in
                Chilean political YouTube follows similar patterns to
                international findings.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Bots are {(botSummary.avgCommentsPerBot / botSummary.avgCommentsPerHuman).toFixed(1)}x more active.
                </strong>{" "}
                Each bot account averages {botSummary.avgCommentsPerBot}{" "}
                comments vs {botSummary.avgCommentsPerHuman} for human accounts,
                often posting the same or very similar text across multiple
                videos.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Cross-video duplication is the strongest signal.
                </strong>{" "}
                Users who post identical comments across different videos are
                overwhelmingly likely to be automated. This aligns with the
                Levenshtein-based duplicate detection used by the YT-Spammer-Purge
                project.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Both political sides are targeted.
                </strong>{" "}
                Bot categories include astroturfing (positive support), attack
                bots (negative insults), and propaganda (copy-paste slogans),
                suggesting orchestrated campaigns rather than organic behavior.
              </li>
            </ul>
          </div>

          <div className="stat-card">
            <h3 className="text-lg font-semibold mb-4 text-yellow-400">
              Limitations
            </h3>
            <ul className="space-y-3 text-sm text-[var(--text-secondary)]">
              <li>
                <strong className="text-[var(--text-primary)]">
                  Heuristic-based, not ML-based.
                </strong>{" "}
                Our bot detection uses curated keyword lists and behavioral
                signals, not trained classifiers. False positives are possible
                for passionate users who comment frequently.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Political leaning is approximate.
                </strong>{" "}
                Left/right classification uses keyword co-occurrence, not
                sentiment analysis. A comment saying &quot;los comunistas
                destruyen Chile&quot; is classified as right-leaning based on the
                word &quot;comunistas&quot;, which is correct in context but not nuanced.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Dataset scope.
                </strong>{" "}
                The analysis covers a sample of Chilean political channels, not
                the entirety of Chilean YouTube. Results may not generalize to
                all political content.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">
                  Temporal snapshot.
                </strong>{" "}
                Comments were scraped at a single point in time. Bot activity
                may fluctuate around elections or political events.
              </li>
            </ul>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="text-lg font-semibold mb-3">
            Comparison with FactCheck LT
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="text-left py-2 px-3 text-[var(--text-secondary)]">
                    Metric
                  </th>
                  <th className="text-right py-2 px-3 text-blue-400">
                    Our Study
                  </th>
                  <th className="text-right py-2 px-3 text-purple-400">
                    FactCheck LT
                  </th>
                </tr>
              </thead>
              <tbody className="text-[var(--text-secondary)]">
                <tr className="border-b border-[var(--border)]/50">
                  <td className="py-2 px-3">Bot accounts (% of users)</td>
                  <td className="py-2 px-3 text-right font-semibold text-[var(--text-primary)]">
                    {botSummary.botAccountPct}%
                  </td>
                  <td className="py-2 px-3 text-right">&lt;1%</td>
                </tr>
                <tr className="border-b border-[var(--border)]/50">
                  <td className="py-2 px-3">
                    Bot comment volume (% of comments)
                  </td>
                  <td className="py-2 px-3 text-right font-semibold text-[var(--text-primary)]">
                    {botSummary.botCommentVolumePct}%
                  </td>
                  <td className="py-2 px-3 text-right">11.6%</td>
                </tr>
                <tr className="border-b border-[var(--border)]/50">
                  <td className="py-2 px-3">Comments analyzed</td>
                  <td className="py-2 px-3 text-right font-semibold text-[var(--text-primary)]">
                    {botSummary.totalComments.toLocaleString()}
                  </td>
                  <td className="py-2 px-3 text-right">94,532</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="text-center mt-12 space-y-3">
          <a
            href="https://github.com/Dyotson/ChileYoutubeNewsAnalyzer"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors border border-[var(--border)] rounded-full px-5 py-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
            </svg>
            Full source code, data &amp; methodology on GitHub
          </a>
          <p className="text-xs text-[var(--text-secondary)]">
            Research by Maximiliano Militzer &middot; Built with Next.js,
            youtube-comment-downloader, scrapetube &middot; Data analyzed with Python
          </p>
        </div>
      </div>
    </section>
  );
}

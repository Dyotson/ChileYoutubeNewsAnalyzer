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

        <p className="text-center text-xs text-[var(--text-secondary)] mt-12">
          Research by Maximiliano Militzer &middot; Built with Next.js,
          youtube-comment-downloader, scrapetube &middot; Data analyzed with Python
        </p>
      </div>
    </section>
  );
}

"use client";

interface BotAccount {
  author: string;
  totalComments: number;
  flaggedComments: number;
  maxScore: number;
  videosIn: number;
  avgScore: number;
}

interface TopBotsTableProps {
  bots: BotAccount[];
}

export default function TopBotsTable({ bots }: TopBotsTableProps) {
  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Top Suspected Bot Accounts</h2>
        <p className="section-subtitle">
          Top 20 accounts ranked by maximum bot score
        </p>

        <div className="stat-card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left py-3 px-3 text-[var(--text-secondary)] font-medium">
                  #
                </th>
                <th className="text-left py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Account
                </th>
                <th className="text-right py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Max Score
                </th>
                <th className="text-right py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Total Comments
                </th>
                <th className="text-right py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Flagged
                </th>
                <th className="text-right py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Videos
                </th>
                <th className="text-right py-3 px-3 text-[var(--text-secondary)] font-medium">
                  Avg Score
                </th>
              </tr>
            </thead>
            <tbody>
              {bots.slice(0, 20).map((bot, i) => (
                <tr
                  key={bot.author}
                  className="border-b border-[var(--border)]/50 hover:bg-[var(--bg-card-hover)] transition-colors"
                >
                  <td className="py-2.5 px-3 text-[var(--text-secondary)]">
                    {i + 1}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-xs">
                    {bot.author}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <span
                      className={`font-semibold ${
                        bot.maxScore >= 0.8
                          ? "text-red-400"
                          : bot.maxScore >= 0.6
                            ? "text-orange-400"
                            : "text-yellow-400"
                      }`}
                    >
                      {bot.maxScore.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    {bot.totalComments}
                  </td>
                  <td className="py-2.5 px-3 text-right text-red-400">
                    {bot.flaggedComments}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    {bot.videosIn}
                  </td>
                  <td className="py-2.5 px-3 text-right text-[var(--text-secondary)]">
                    {bot.avgScore.toFixed(3)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

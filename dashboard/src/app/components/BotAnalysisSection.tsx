"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

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

interface CategoryItem {
  name: string;
  value: number;
}

interface VideoItem {
  video: string;
  total: number;
  bots: number;
  pct: number;
}

interface BotAnalysisSectionProps {
  botSummary: BotSummary;
  categories: CategoryItem[];
  videoSummary: VideoItem[];
}

const CAT_COLORS = ["#ef4444", "#f97316", "#a855f7", "#3b82f6", "#eab308"];

export default function BotAnalysisSection({
  botSummary,
  categories,
  videoSummary,
}: BotAnalysisSectionProps) {
  const comparisonData = [
    {
      label: "Accounts",
      bots: botSummary.botAccountPct,
      humans: 100 - botSummary.botAccountPct,
    },
    {
      label: "Comments",
      bots: botSummary.botCommentVolumePct,
      humans: 100 - botSummary.botCommentVolumePct,
    },
  ];

  const topVideos = videoSummary
    .filter((v) => v.bots > 0)
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 20);

  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Bot Detection Results</h2>
        <p className="section-subtitle">
          FactCheck-style account vs. comment volume analysis
        </p>

        <div className="grid md:grid-cols-3 gap-4 mb-10">
          <div className="stat-card text-center">
            <p className="text-4xl font-bold text-red-400">
              {botSummary.botAccountPct}%
            </p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              of accounts are bots
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-4xl font-bold text-red-400">
              {botSummary.botCommentVolumePct}%
            </p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              of comments are by bots
            </p>
          </div>
          <div className="stat-card text-center">
            <p className="text-4xl font-bold text-yellow-400">
              {botSummary.avgCommentsPerBot}x
            </p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              more active than humans (
              {botSummary.avgCommentsPerBot} vs {botSummary.avgCommentsPerHuman}{" "}
              avg)
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-10">
          <div className="stat-card">
            <h3 className="font-semibold mb-4">Accounts vs Comment Volume</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={comparisonData} layout="vertical">
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "#9898b0", fontSize: 12 }} />
                <YAxis dataKey="label" type="category" tick={{ fill: "#e8e8f0", fontSize: 13 }} width={80} />
                <Tooltip
                  contentStyle={{ background: "#1a1a26", border: "1px solid #2a2a3a", borderRadius: 8 }}
                  formatter={(v) => `${Number(v).toFixed(1)}%`}
                />
                <Bar dataKey="bots" stackId="a" fill="#ef4444" name="Bots" radius={[0, 0, 0, 0]} />
                <Bar dataKey="humans" stackId="a" fill="#2a2a3a" name="Humans" radius={[0, 4, 4, 0]} />
                <Legend />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="stat-card">
            <h3 className="font-semibold mb-4">Bot Categories</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={categories.filter((c) => c.value > 0)}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {categories.map((_, i) => (
                    <Cell
                      key={i}
                      fill={CAT_COLORS[i % CAT_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#1a1a26", border: "1px solid #2a2a3a", borderRadius: 8 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="font-semibold mb-4">
            Bot Percentage by Video (top 20 most affected)
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={topVideos}>
              <XAxis
                dataKey="video"
                tick={{ fill: "#9898b0", fontSize: 9 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fill: "#9898b0", fontSize: 12 }} unit="%" />
              <Tooltip
                contentStyle={{ background: "#1a1a26", border: "1px solid #2a2a3a", borderRadius: 8 }}
                  formatter={(v) => `${v}%`}
                  labelFormatter={(l) => `Video: ${l}`}
              />
              <Bar dataKey="pct" fill="#ef4444" radius={[4, 4, 0, 0]} name="Bot %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

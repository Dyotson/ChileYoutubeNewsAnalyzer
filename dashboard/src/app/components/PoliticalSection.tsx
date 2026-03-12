"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Legend,
} from "recharts";

interface PoliticalOverall {
  left: number;
  right: number;
  neutral: number;
  leftPct: number;
  rightPct: number;
  neutralPct: number;
}

interface PoliticalVideo {
  video: string;
  total: number;
  left: number;
  right: number;
  neutral: number;
  leftPct: number;
  rightPct: number;
}

interface PoliticalSectionProps {
  overall: PoliticalOverall;
  perVideo: PoliticalVideo[];
}

const PIE_COLORS = ["#3b82f6", "#ef4444", "#4b5563"];

export default function PoliticalSection({
  overall,
  perVideo,
}: PoliticalSectionProps) {
  const pieData = [
    { name: "Left", value: overall.left },
    { name: "Right", value: overall.right },
    { name: "Neutral", value: overall.neutral },
  ];

  const topVideos = perVideo
    .filter((v) => v.leftPct + v.rightPct > 0)
    .sort((a, b) => b.leftPct + b.rightPct - (a.leftPct + a.rightPct))
    .slice(0, 20);

  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Political Leaning</h2>
        <p className="section-subtitle">
          Keyword-based classification of comments into left, right, or neutral
        </p>

        <div className="grid md:grid-cols-2 gap-6 mb-10">
          <div className="stat-card">
            <h3 className="font-semibold mb-4">Overall Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) =>
                    `${name} ${((percent ?? 0) * 100).toFixed(1)}%`
                  }
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#1a1a26",
                    border: "1px solid #2a2a3a",
                    borderRadius: 8,
                  }}
                  formatter={(v) => Number(v).toLocaleString()}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-col justify-center gap-4">
            <div className="stat-card flex items-center gap-4">
              <div
                className="w-4 h-4 rounded-full shrink-0"
                style={{ background: "#3b82f6" }}
              />
              <div>
                <p className="text-2xl font-bold">{overall.leftPct}%</p>
                <p className="text-sm text-[var(--text-secondary)]">
                  Left-leaning ({overall.left.toLocaleString()} comments)
                </p>
              </div>
            </div>
            <div className="stat-card flex items-center gap-4">
              <div
                className="w-4 h-4 rounded-full shrink-0"
                style={{ background: "#ef4444" }}
              />
              <div>
                <p className="text-2xl font-bold">{overall.rightPct}%</p>
                <p className="text-sm text-[var(--text-secondary)]">
                  Right-leaning ({overall.right.toLocaleString()} comments)
                </p>
              </div>
            </div>
            <div className="stat-card flex items-center gap-4">
              <div
                className="w-4 h-4 rounded-full shrink-0"
                style={{ background: "#4b5563" }}
              />
              <div>
                <p className="text-2xl font-bold">{overall.neutralPct}%</p>
                <p className="text-sm text-[var(--text-secondary)]">
                  Neutral / unclassified (
                  {overall.neutral.toLocaleString()} comments)
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="font-semibold mb-4">
            Political Leaning by Video (top 20 most politically active)
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
                contentStyle={{
                  background: "#1a1a26",
                  border: "1px solid #2a2a3a",
                  borderRadius: 8,
                }}
                formatter={(v) => `${v}%`}
              />
              <Legend />
              <Bar
                dataKey="leftPct"
                stackId="a"
                fill="#3b82f6"
                name="Left %"
              />
              <Bar
                dataKey="rightPct"
                stackId="a"
                fill="#ef4444"
                name="Right %"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

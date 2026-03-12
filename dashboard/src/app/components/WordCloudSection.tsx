"use client";

import { useEffect, useRef, useState } from "react";

interface WordItem {
  text: string;
  value: number;
}

interface WordCloudSectionProps {
  words: WordItem[];
}

interface LayoutWord {
  text: string;
  size: number;
  value: number;
  x: number;
  y: number;
  rotate: number;
}

const COLORS = [
  "#ef4444",
  "#3b82f6",
  "#22c55e",
  "#eab308",
  "#a855f7",
  "#f97316",
  "#06b6d4",
  "#ec4899",
];

export default function WordCloudSection({ words }: WordCloudSectionProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [layoutWords, setLayoutWords] = useState<LayoutWord[]>([]);
  const [tooltip, setTooltip] = useState<{
    text: string;
    value: number;
    x: number;
    y: number;
  } | null>(null);

  useEffect(() => {
    async function buildCloud() {
      const cloud = (await import("d3-cloud")).default;
      const width = containerRef.current?.clientWidth || 800;
      const height = 500;

      const maxVal = Math.max(...words.map((w) => w.value));
      const minVal = Math.min(...words.map((w) => w.value));
      const scale = (v: number) =>
        12 + ((v - minVal) / (maxVal - minVal)) * 64;

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const layout = (cloud as any)()
        .size([width, height])
        .words(words.map((w) => ({ text: w.text, value: w.value, size: scale(w.value) })))
        .padding(3)
        .rotate(() => (Math.random() > 0.7 ? 90 : 0))
        .font("Inter")
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .fontSize((d: any) => d.size)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .on("end", (output: any[]) => {
          setLayoutWords(
            output.map((w) => ({
              text: w.text,
              size: w.size,
              value: w.value,
              x: w.x,
              y: w.y,
              rotate: w.rotate,
            }))
          );
        });
      layout.start();
    }
    if (words.length > 0) buildCloud();
  }, [words]);

  const width = 800;
  const height = 500;

  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="section-title">Most Used Words</h2>
        <p className="section-subtitle">
          Top 200 words across all comments (Spanish stopwords filtered)
        </p>
        <div
          ref={containerRef}
          className="stat-card relative overflow-hidden"
          style={{ minHeight: 500 }}
        >
          {layoutWords.length > 0 && (
            <svg
              viewBox={`${-width / 2} ${-height / 2} ${width} ${height}`}
              className="w-full"
              style={{ height: 500 }}
            >
              {layoutWords.map((w, i) => (
                <text
                  key={w.text}
                  textAnchor="middle"
                  transform={`translate(${w.x},${w.y}) rotate(${w.rotate})`}
                  style={{
                    fontSize: w.size,
                    fontFamily: "Inter, sans-serif",
                    fontWeight: w.size > 40 ? 700 : 500,
                    fill: COLORS[i % COLORS.length],
                    cursor: "pointer",
                    transition: "opacity 0.15s",
                  }}
                  opacity={0.85}
                  onMouseEnter={(e) => {
                    (e.target as SVGTextElement).style.opacity = "1";
                    const rect = (
                      e.target as SVGTextElement
                    ).getBoundingClientRect();
                    setTooltip({
                      text: w.text,
                      value: w.value,
                      x: rect.left + rect.width / 2,
                      y: rect.top - 10,
                    });
                  }}
                  onMouseLeave={(e) => {
                    (e.target as SVGTextElement).style.opacity = "0.85";
                    setTooltip(null);
                  }}
                >
                  {w.text}
                </text>
              ))}
            </svg>
          )}
          {tooltip && (
            <div
              className="fixed z-50 bg-black/90 text-white text-xs px-3 py-1.5 rounded-lg pointer-events-none"
              style={{
                left: tooltip.x,
                top: tooltip.y,
                transform: "translate(-50%, -100%)",
              }}
            >
              <strong>{tooltip.text}</strong>: {tooltip.value.toLocaleString()}{" "}
              mentions
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

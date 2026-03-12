#!/usr/bin/env node
/**
 * Converts the Python analyzer's CSV output into static JSON files
 * consumed by the Next.js dashboard at build time.
 *
 * Usage: node scripts/prepare-data.js [csv-dir] [json-dir]
 */
const fs = require("fs");
const path = require("path");
const { parse } = require("csv-parse/sync");

const CSV_DIR = process.argv[2] || path.resolve(__dirname, "../../output");
const OUT_DIR = process.argv[3] || path.resolve(__dirname, "../public/data");

function readCsv(filename) {
  const filepath = path.join(CSV_DIR, filename);
  if (!fs.existsSync(filepath)) {
    console.warn(`  [WARN] ${filepath} not found, skipping.`);
    return [];
  }
  const raw = fs.readFileSync(filepath, "utf-8");
  return parse(raw, { columns: true, skip_empty_lines: true });
}

function writeJson(filename, data) {
  const filepath = path.join(OUT_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  console.log(`  -> ${filepath}`);
}

fs.mkdirSync(OUT_DIR, { recursive: true });
console.log(`Reading CSVs from: ${CSV_DIR}`);
console.log(`Writing JSON to:   ${OUT_DIR}\n`);

// --- Word frequency (top 200) ---
const words = readCsv("word_frequency.csv").slice(0, 200).map((r) => ({
  text: r.word,
  value: Number(r.count),
}));
writeJson("word_frequency.json", words);

// --- Bot volume summary (FactCheck-style stats) ---
const botVolume = readCsv("bot_volume_summary.csv");
const botAccounts = botVolume.filter((r) => r.is_bot_account === "True");
const humanAccounts = botVolume.filter((r) => r.is_bot_account === "False");
const totalComments = botVolume.reduce((s, r) => s + Number(r.total_comments), 0);
const botCommentVolume = botAccounts.reduce((s, r) => s + Number(r.total_comments), 0);

writeJson("bot_summary.json", {
  totalAccounts: botVolume.length,
  totalComments,
  botAccounts: botAccounts.length,
  botAccountPct: Number(((botAccounts.length / botVolume.length) * 100).toFixed(2)),
  botCommentVolume,
  botCommentVolumePct: Number(((botCommentVolume / totalComments) * 100).toFixed(2)),
  avgCommentsPerBot: botAccounts.length
    ? Number((botCommentVolume / botAccounts.length).toFixed(1))
    : 0,
  avgCommentsPerHuman: humanAccounts.length
    ? Number(
        (
          humanAccounts.reduce((s, r) => s + Number(r.total_comments), 0) /
          humanAccounts.length
        ).toFixed(1)
      )
    : 0,
});

// --- Bot categories from video_summary TOTAL row ---
const videoSummary = readCsv("video_summary.csv");
const totalRow = videoSummary.find((r) => r.video_url === "TOTAL");
if (totalRow) {
  writeJson("bot_categories.json", [
    { name: "Astroturfing", value: Number(totalRow.astroturfing_count) },
    { name: "Attack Bot", value: Number(totalRow.attack_bot_count) },
    { name: "Propaganda", value: Number(totalRow.propaganda_count) },
    { name: "Spam", value: Number(totalRow.spam_count) },
    { name: "Mixed", value: Number(totalRow.mixed_count) },
  ]);
}

// --- Per-video summary (exclude TOTAL, top 30 by comment count) ---
const perVideo = videoSummary
  .filter((r) => r.video_url !== "TOTAL")
  .map((r) => ({
    video: r.video_url.replace("https://www.youtube.com/watch?v=", ""),
    total: Number(r.total_comments),
    bots: Number(r.suspected_bots),
    pct: Number(r.bot_percentage),
  }))
  .sort((a, b) => b.total - a.total)
  .slice(0, 30);
writeJson("video_summary.json", perVideo);

// --- Political summary ---
const political = readCsv("political_summary.csv");
const polTotal = political.find((r) => r.video_url === "TOTAL");
if (polTotal) {
  writeJson("political_summary.json", {
    overall: {
      left: Number(polTotal.left_count),
      right: Number(polTotal.right_count),
      neutral: Number(polTotal.neutral_count),
      leftPct: Number(polTotal.left_pct),
      rightPct: Number(polTotal.right_pct),
      neutralPct: Number(polTotal.neutral_pct),
    },
    perVideo: political
      .filter((r) => r.video_url !== "TOTAL")
      .map((r) => ({
        video: r.video_url.replace("https://www.youtube.com/watch?v=", ""),
        total: Number(r.total_comments),
        left: Number(r.left_count),
        right: Number(r.right_count),
        neutral: Number(r.neutral_count),
        leftPct: Number(r.left_pct),
        rightPct: Number(r.right_pct),
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 30),
  });
}

// --- Top bot accounts ---
const topBots = botAccounts
  .sort((a, b) => Number(b.max_bot_score) - Number(a.max_bot_score))
  .slice(0, 30)
  .map((r) => ({
    author: r.author,
    totalComments: Number(r.total_comments),
    flaggedComments: Number(r.flagged_comments),
    maxScore: Number(r.max_bot_score),
    videosIn: Number(r.videos_appeared_in),
    avgScore: Number(r.avg_bot_score),
  }));
writeJson("top_bots.json", topBots);

console.log("\nDone.");

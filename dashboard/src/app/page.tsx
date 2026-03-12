import HeroSection from "./components/HeroSection";
import MethodologySection from "./components/MethodologySection";
import WordCloudSection from "./components/WordCloudSection";
import BotAnalysisSection from "./components/BotAnalysisSection";
import PoliticalSection from "./components/PoliticalSection";
import TopBotsTable from "./components/TopBotsTable";
import ConclusionsSection from "./components/ConclusionsSection";

import wordFrequency from "../../public/data/word_frequency.json";
import botSummary from "../../public/data/bot_summary.json";
import botCategories from "../../public/data/bot_categories.json";
import videoSummary from "../../public/data/video_summary.json";
import politicalSummary from "../../public/data/political_summary.json";
import topBots from "../../public/data/top_bots.json";

export default function Home() {
  return (
    <main className="min-h-screen">
      <HeroSection
        botSummary={botSummary}
        videoCount={videoSummary.length}
      />
      <MethodologySection />
      <WordCloudSection words={wordFrequency} />
      <BotAnalysisSection
        botSummary={botSummary}
        categories={botCategories}
        videoSummary={videoSummary}
      />
      <PoliticalSection
        overall={politicalSummary.overall}
        perVideo={politicalSummary.perVideo}
      />
      <TopBotsTable bots={topBots} />
      <ConclusionsSection botSummary={botSummary} />
    </main>
  );
}

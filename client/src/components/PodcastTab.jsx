import React from "react";
import ReactMarkdown from "react-markdown";
import { Loader2, Headphones, Play, Pause } from "lucide-react";

const PodcastTab = ({ podcastScript, isPlaying, togglePlayback, podcastLang, setPodcastLang, generatePodcast, loading }) => {
  return (
    <div className="h-full overflow-y-auto p-8 flex flex-col items-center scrollbar-thin">
      {!podcastScript ? (
        <div className="text-center mt-20 max-w-md">
          <div className="bg-green-900/20 p-6 rounded-full mb-6 inline-block">
             <Headphones size={64} className="text-green-400"/>
          </div>
          <h3 className="text-2xl font-bold text-gray-300 mb-6">AI Audio Summary</h3>
          
          <div className="bg-gray-800 p-1.5 rounded-full inline-flex mb-8 border border-gray-700">
            <button onClick={() => setPodcastLang('english')} className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${podcastLang === 'english' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}>
              English
            </button>
            <button onClick={() => setPodcastLang('hinglish')} className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${podcastLang === 'hinglish' ? 'bg-orange-600 text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}>
              Hinglish
            </button>
          </div>

          <button onClick={generatePodcast} disabled={loading} className="bg-green-600 w-full px-6 py-4 rounded-xl font-bold hover:bg-green-500 flex justify-center items-center gap-2 shadow-lg shadow-green-900/20 transition-all hover:scale-105">
            {loading ? <Loader2 className="animate-spin" /> : <Headphones />} Generate Podcast
          </button>
        </div>
      ) : (
        <div className="w-full max-w-3xl">
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-6 rounded-2xl border border-gray-700 shadow-xl mb-6 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                 <div className={`w-3 h-3 rounded-full ${isPlaying ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                 Now Playing
              </h3>
              <p className="text-sm text-gray-400 mt-1">{podcastLang === 'hinglish' ? 'Hinglish Conversation' : 'Standard English'} • AI Hosts</p>
            </div>
            <button onClick={togglePlayback} className="bg-white text-black w-14 h-14 rounded-full flex items-center justify-center hover:scale-110 transition shadow-lg shadow-white/10">
              {isPlaying ? <Pause fill="black" size={24} /> : <Play fill="black" className="ml-1" size={24} />}
            </button>
          </div>

          <div className="space-y-4 font-mono text-sm leading-relaxed text-gray-300 bg-gray-900/50 p-8 rounded-2xl border border-gray-800 shadow-inner">
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown>{podcastScript}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PodcastTab;
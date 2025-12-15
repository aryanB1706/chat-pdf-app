import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Sparkles, Loader2 } from "lucide-react";

const ChatTab = ({ messages, input, setInput, handleSend, loading, mode, setMode }) => {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl p-4 leading-relaxed shadow-md ${
                msg.role === 'user'
                  ? 'bg-[#1e293b] text-blue-100 border border-gray-700'
                  : 'bg-transparent text-gray-200'
              }`}
            >
              {msg.role === 'bot' && (
                <div className="flex items-center gap-2 mb-2 text-blue-400 font-bold text-xs uppercase tracking-wider">
                  <Sparkles size={12} /> AI Answer
                </div>
              )}
              <div className="prose prose-invert text-sm">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
            <Loader2 className="animate-spin" size={16} /> Thinking...
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#131620] border-t border-gray-800">
        <div className="flex justify-center gap-2 mb-3">
          <button onClick={() => setMode('full')} className={`text-xs px-3 py-1 rounded-full border transition-all ${mode === 'full' ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'border-gray-700 text-gray-500 hover:bg-gray-800'}`}>
            Full PDF
          </button>
          <button onClick={() => setMode('crop')} className={`text-xs px-3 py-1 rounded-full border transition-all ${mode === 'crop' ? 'bg-green-600/20 border-green-500 text-green-400' : 'border-gray-700 text-gray-500 hover:bg-gray-800'}`}>
            Crop & Ask
          </button>
        </div>
        
        <div className="flex gap-2 items-center bg-[#1e2330] p-2 rounded-xl border border-gray-700 focus-within:border-blue-500 transition-colors">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={mode === 'crop' ? "Select area on left, then ask..." : "Ask anything about your PDF..."}
            className="flex-1 bg-transparent border-none outline-none text-gray-200 px-3 py-2 text-sm placeholder-gray-500"
          />
          <button onClick={handleSend} disabled={loading} className="bg-blue-600 hover:bg-blue-500 text-white p-2.5 rounded-lg transition-all disabled:opacity-50">
            <Send size={18} />
          </button>
        </div>
        <p className="text-center text-[10px] text-gray-600 mt-2">Gemini 1.5 Flash • AI can make mistakes</p>
      </div>
    </div>
  );
};

export default ChatTab;
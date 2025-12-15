import React, { useState, useEffect } from "react";
import axios from "axios";
import { pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import "react-image-crop/dist/ReactCrop.css";
import { Layers, CheckCircle, BrainCircuit, Headphones } from "lucide-react";

// Components Import
import PDFViewer from "./components/PDFViewer";
import ChatTab from "./components/ChatTab";
import QuizTab from "./components/QuizTab";
import MindMapTab from "./components/MindMapTab";
import PodcastTab from "./components/PodcastTab";

// Worker Setup
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat'); // Tabs: chat, quiz, mindmap, podcast

  // Chat State
  const [messages, setMessages] = useState([{ role: 'bot', text: "Hi! Upload a PDF to unlock Chat, Quiz, Mind Maps & Podcasts!" }]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState('full');

  // Crop State
  const [crop, setCrop] = useState();
  const [completedCrop, setCompletedCrop] = useState(null);

  // Feature Data States
  const [quizData, setQuizData] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [mindMapNodes, setMindMapNodes] = useState([]);
  const [mindMapEdges, setMindMapEdges] = useState([]);
  const [podcastScript, setPodcastScript] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [podcastLang, setPodcastLang] = useState("english");

  // --- HANDLERS (Same Logic as before, kept here for central state management) ---
  
  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPdfUrl(URL.createObjectURL(selectedFile));
      const formData = new FormData();
      formData.append("file", selectedFile);
      try {
        setLoading(true);
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/upload`, formData);
        setNumPages(res.data.totalPages);
        setMessages(prev => [...prev, { role: 'bot', text: `PDF Processed! Detected ${res.data.totalPages} pages.` }]);
      } catch (err) { alert("Upload failed"); } finally { setLoading(false); }
    }
  };

  const getCroppedImg = async () => {
    if (!completedCrop) return;
    const pdfCanvas = document.querySelector('.react-pdf__Page__canvas');
    if (!pdfCanvas) return;
    const scaleX = pdfCanvas.width / pdfCanvas.offsetWidth;
    const scaleY = pdfCanvas.height / pdfCanvas.offsetHeight;
    const canvas = document.createElement("canvas");
    canvas.width = completedCrop.width * scaleX;
    canvas.height = completedCrop.height * scaleY;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(pdfCanvas, completedCrop.x * scaleX, completedCrop.y * scaleY, completedCrop.width * scaleX, completedCrop.height * scaleY, 0, 0, completedCrop.width * scaleX, completedCrop.height * scaleY);
    return canvas.toDataURL("image/png");
  };

  const handleSend = async () => {
    if (!input.trim() && mode !== 'crop') return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: "user", text: userMsg || (mode === 'crop' ? "Analyze this selection" : "") }]);
    setInput("");
    setLoading(true);

    try {
      let response;
      if (mode === 'crop') {
        const base64 = await getCroppedImg();
        if (!base64) { alert("Select area first!"); setLoading(false); return; }
        response = await axios.post(`${import.meta.env.VITE_API_URL}/analyze-crop`, { image: base64, question: userMsg });
        setCrop(undefined);
      } else {
        response = await axios.post(`${import.meta.env.VITE_API_URL}/chat`, { question: userMsg });
      }
      setMessages(prev => [...prev, { role: "bot", text: response.data.reply }]);
    } catch (error) { setMessages(prev => [...prev, { role: "bot", text: "Error fetching response." }]); } finally { setLoading(false); }
  };

  const generateQuiz = async () => {
    setLoading(true);
    try {
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/quiz`);
        setQuizData(res.data);
        setQuizAnswers({});
    } catch (err) { alert("Quiz Gen Error"); } finally { setLoading(false); }
  };

  const generateMindMap = async () => {
    setLoading(true);
    try {
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/mindmap`);
        setMindMapNodes(res.data.nodes || []);
        setMindMapEdges(res.data.edges || []);
    } catch (err) { alert("Mind Map Error"); } finally { setLoading(false); }
  };

  const generatePodcast = async () => {
    setLoading(true);
    try {
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/podcast`, { language: podcastLang });
        setPodcastScript(res.data.script);
    } catch (err) { alert("Podcast Error"); } finally { setLoading(false); }
  };

  const togglePlayback = () => {
    if (isPlaying) {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
    } else {
        const utterance = new SpeechSynthesisUtterance(podcastScript);
        const voices = window.speechSynthesis.getVoices();
        if (podcastLang === 'hinglish') {
           const hindiVoice = voices.find(v => v.lang.includes('hi'));
           if (hindiVoice) utterance.voice = hindiVoice;
        }
        utterance.onend = () => setIsPlaying(false);
        window.speechSynthesis.speak(utterance);
        setIsPlaying(true);
    }
  };

  return (
    <div className="flex h-screen bg-[#0b0f19] text-gray-100 font-sans overflow-hidden">
      
      {/* 1. Left Side: PDF Viewer Component */}
      <PDFViewer 
        file={file} pdfUrl={pdfUrl} numPages={numPages} pageNumber={pageNumber} 
        setPageNumber={setPageNumber} onFileChange={handleFileChange} 
        mode={mode} crop={crop} setCrop={setCrop} setCompletedCrop={setCompletedCrop} 
        loading={loading}
      />

      {/* 2. Right Side: Tabs & Features */}
      <div className="flex-1 flex flex-col bg-[#0b0f19]">
        
        {/* Navigation Tabs */}
        <div className="flex border-b border-gray-800 bg-[#131620]">
            {[
              { id: 'chat', label: 'Chat', icon: Layers },
              { id: 'quiz', label: 'Quiz', icon: CheckCircle },
              { id: 'mindmap', label: 'Mind Map', icon: BrainCircuit },
              { id: 'podcast', label: 'Podcast', icon: Headphones },
            ].map((tab) => (
                <button 
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 py-4 text-sm font-medium flex justify-center items-center gap-2 transition-all border-b-2 
                    ${activeTab === tab.id ? 'border-blue-500 text-blue-400 bg-blue-500/10' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
                >
                    <tab.icon size={16}/> {tab.label}
                </button>
            ))}
        </div>

        {/* Content Area - Render Component Based on Active Tab */}
        <div className="flex-1 overflow-hidden relative">
            
            {activeTab === 'chat' && (
              <ChatTab 
                messages={messages} input={input} setInput={setInput} 
                handleSend={handleSend} loading={loading} mode={mode} setMode={setMode} 
              />
            )}

            {activeTab === 'quiz' && (
              <QuizTab 
                quizData={quizData} quizAnswers={quizAnswers} setQuizAnswers={setQuizAnswers} 
                generateQuiz={generateQuiz} loading={loading} 
              />
            )}

            {activeTab === 'mindmap' && (
              <MindMapTab 
                mindMapNodes={mindMapNodes} mindMapEdges={mindMapEdges} 
                generateMindMap={generateMindMap} loading={loading} 
              />
            )}

            {activeTab === 'podcast' && (
              <PodcastTab 
                podcastScript={podcastScript} isPlaying={isPlaying} togglePlayback={togglePlayback}
                podcastLang={podcastLang} setPodcastLang={setPodcastLang} generatePodcast={generatePodcast} 
                loading={loading}
              />
            )}

        </div>
      </div>
    </div>
  );
}

export default App;
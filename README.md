# 🧠 Chat with PDF – AI Study Companion

A powerful **Full-Stack AI Application** that transforms static PDF documents into **interactive study materials**.  
Unlike standard chatbots, this platform offers **Multimodal learning**, **Visual understanding**, and **Audio-based revision** — designed especially for students.

🔗 **Live Demo:** https://chat-pdf-app-sage.vercel.app/

---

## 🚀 Key Features

### 1. 💬 Context-Aware Chat & Reasoning
- **Full PDF Mode** – Ask questions from the entire document  
- **Page Range Mode** – Query specific sections (e.g., *“Summarize pages 1–5”*)  
- **Conversation Memory** – Supports follow-up questions with context retention  

---

### 2. 📝 AI Quiz Generator (Exam Mode)
- Auto-generates **MCQs** directly from the uploaded PDF  
- **Instant answer validation**  
- **Detailed explanations** for each question  
- Ideal for **exam preparation & revision**

---

### 3. 🧠 Visual Mind Maps (React Flow)
- Converts complex text into **interactive mind maps**  
- Displays **topic hierarchy** using nodes & edges  
- Improves concept clarity and retention  

---

### 4. 🎧 AI Podcast with Human Voice
- Generates a **conversational podcast script** from the PDF  
- **Hinglish Mode** (Hindi + English mix)  
- High-quality, natural speech using **ElevenLabs / Google TTS**  
- Perfect for **audio-based learning & revision**

---

### 5. ✂️ Multimodal “Crop & Ask”
- Crop any **diagram, formula, or graph** directly from the PDF  
- AI analyzes the **visual content** using Vision capabilities  
- Provides **detailed explanations** of the cropped region  

---

## 🛠️ Tech Stack

### Frontend
- **React.js (Vite)** – Fast, modern UI  
- **Tailwind CSS** – Responsive dark-themed design  
- **React Flow** – Mind map visualization  
- **React PDF & React Crop** – PDF rendering & cropping  
- **Lucide React** – Clean, lightweight icons  

---

### Backend (MVC Architecture)
- **Node.js & Express.js** – RESTful API  
- **Multer** – File upload & buffer handling  
- **PDF2JSON** – Accurate PDF text extraction  

---

### AI Services
- **Google Gemini 1.5 Flash** –  
  Text reasoning, summarization, quiz generation, and image analysis  
- **ElevenLabs API** –  
  Human-like Hinglish audio generation  

---

## 📂 Project Structure

```bash
chat-pdf-app/
├── client/ (Frontend)
│   ├── src/
│   │   ├── components/     # ChatTab, QuizTab, MindMapTab
│   │   ├── App.jsx         # Global State Management
│   │   └── main.jsx        # Entry Point
│
├── server/ (Backend)
│   ├── config/             # AI & Safety Configuration
│   ├── controllers/        # Business Logic
│   ├── routes/             # API Routes
│   ├── utils/              # PDF Parsing Utilities
│   └── index.js            # Server Entry Point

```

## ⚙️ Installation & Run Locally

Follow these steps to set up the project on your local machine.

Prerequisites

Node.js installed

Google Gemini API Key

(Optional) ElevenLabs API Key

## 1. Clone the Repository

git clone [https://github.com/YOUR_GITHUB_USERNAME/chat-pdf-app.git](https://github.com/YOUR_GITHUB_USERNAME/chat-pdf-app.git)
cd chat-pdf-app


## 2. Backend Setup

cd server
npm install


Create a .env file in the server folder:

PORT=5000
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here


Start the Server:

node index.js


## 3. Frontend Setup

Open a new terminal:

cd client
npm install


Create a .env file in the client folder:

VITE_API_URL=http://localhost:5000


Start the Client:

npm run dev


Visit http://localhost:5173 in your browser.


🤝 Contributing

Contributions are welcome!

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License

This project is licensed under the MIT License.

👨‍💻 Author

[Aryan Kumar]

GitHub: https://github.com/aryanB1706

LinkedIn: https://www.linkedin.com/in/aryan7k/

Email: aryankumarbndm0@gmail.com

Made with ❤️ using MERN Stack & Generative AI
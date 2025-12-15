const { model, jsonModel } = require("../config/gemini");
const { getPdfPages } = require("./fileController");

// --- Helper to get context ---
const getContext = (startPage, endPage) => {
    const pdfPages = getPdfPages();
    if (pdfPages.length === 0) return null;
    
    if (startPage && endPage) {
        return pdfPages.slice(startPage - 1, endPage).join("\n\n");
    }
    return pdfPages.join("\n\n");
};

// 1. Chat Logic
const chatWithPDF = async (req, res) => {
    const { question, startPage, endPage } = req.body;
    const context = getContext(startPage, endPage);
    
    if (!context) return res.status(400).json({ error: "Upload PDF first." });

    try {
        const prompt = `Context: """${context.substring(0, 80000)}""" \n\n Question: ${question}`;
        const result = await model.generateContent(prompt);
        res.json({ reply: result.response.text() });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

// 2. Crop Analysis Logic
const analyzeCrop = async (req, res) => {
    const { image, question } = req.body;
    try {
        const base64Data = image.split(",")[1];
        const result = await model.generateContent([
            { inlineData: { data: base64Data, mimeType: "image/png" } },
            { text: question || "Explain this image." },
        ]);
        res.json({ reply: await result.response.text() });
    } catch (error) {
        res.status(500).json({ error: "Failed to analyze crop" });
    }
};

// 3. Quiz Logic
const generateQuiz = async (req, res) => {
    const context = getContext();
    if (!context) return res.status(400).json({ error: "Upload PDF first." });
    
    try {
        const prompt = `
            Based on the following text, generate 5 multiple choice questions.
            Return purely a JSON array.
            Format: [{ "question": "...", "options": ["..."], "answer": 0, "explanation": "..." }]
            Text: """${context.substring(0, 50000)}"""
        `;
        const result = await jsonModel.generateContent(prompt);
        res.json(JSON.parse(result.response.text()));
    } catch (error) {
        res.status(500).json({ error: "Failed to generate quiz" });
    }
};

// 4. Mind Map Logic
const generateMindMap = async (req, res) => {
    const context = getContext();
    if (!context) return res.status(400).json({ error: "Upload PDF first." });

    try {
        const prompt = `
            Create a hierarchical concept map. Return JSON with 'nodes' and 'edges' for ReactFlow.
            Root at {x: 250, y: 0}.
            Text: """${context.substring(0, 50000)}"""
        `;
        const result = await jsonModel.generateContent(prompt);
        res.json(JSON.parse(result.response.text()));
    } catch (error) {
        res.status(500).json({ error: "Failed to generate mind map" });
    }
};

// 5. Podcast Logic
const generatePodcast = async (req, res) => {
    const { language } = req.body;
    const context = getContext();
    if (!context) return res.status(400).json({ error: "Upload PDF first." });

    try {
        let langInstruction = language === 'hinglish' 
            ? "Use Hinglish (Hindi+English). Fun & casual tone." 
            : "Use clear, engaging English.";

        const prompt = `
            Convert text to a 2-minute podcast script between Host A and Host B.
            ${langInstruction}
            Text: """${context.substring(0, 40000)}"""
        `;
        const result = await model.generateContent(prompt);
        res.json({ script: result.response.text() });
    } catch (error) {
        res.status(500).json({ error: "Failed to generate podcast" });
    }
};

module.exports = { chatWithPDF, analyzeCrop, generateQuiz, generateMindMap, generatePodcast };
const express = require("express");
const multer = require("multer");
const { uploadPDF } = require("../controllers/fileController");
const { 
    chatWithPDF, 
    analyzeCrop, 
    generateQuiz, 
    generateMindMap, 
    generatePodcast 
} = require("../controllers/aiController");

const router = express.Router();
const upload = multer();

// File Routes
router.post("/upload", upload.single("file"), uploadPDF);

// AI Routes
router.post("/chat", chatWithPDF);
router.post("/analyze-crop", analyzeCrop);
router.post("/quiz", generateQuiz);
router.post("/mindmap", generateMindMap);
router.post("/podcast", generatePodcast);

module.exports = router;
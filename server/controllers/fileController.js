const { parsePDF } = require("../utils/pdfParser");

// Global Variable for In-Memory Storage (Demo purpose)
// Note for Interview: "For production, I would use Redis or a Database here."
let pdfPages = []; 

const uploadPDF = async (req, res) => {
    try {
        if (!req.file) return res.status(400).send("No file uploaded");
        
        console.log("Processing PDF...");
        const pages = await parsePDF(req.file.buffer);
        
        // Update global store
        pdfPages.splice(0, pdfPages.length, ...pages);
        
        console.log(`PDF Processed. Pages: ${pdfPages.length}`);
        res.json({ message: "PDF Uploaded", totalPages: pdfPages.length });
    } catch (error) {
        console.error("PDF Error:", error);
        res.status(500).send("Error parsing PDF");
    }
};

// Getter function to access pages in other controllers
const getPdfPages = () => pdfPages;

module.exports = { uploadPDF, getPdfPages };
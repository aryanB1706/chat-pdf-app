const PDFParser = require("pdf2json");

const parsePDF = (buffer) => {
    return new Promise((resolve, reject) => {
        const pdfParser = new PDFParser(this, 1);
        pdfParser.on("pdfParser_dataError", (errData) => reject(errData.parserError));
        pdfParser.on("pdfParser_dataReady", () => {
            const rawText = pdfParser.getRawTextContent();
            // Split pages logic
            const pages = rawText.split(/----------------Page \(\d+\) Break----------------/g);
            resolve(pages.filter(p => p.trim().length > 0));
        });
        pdfParser.parseBuffer(buffer);
    });
};

module.exports = { parsePDF };
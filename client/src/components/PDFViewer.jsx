import React from "react";
import { Document, Page } from "react-pdf";
import ReactCrop from "react-image-crop";
import { FileText, UploadCloud, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";

const PDFViewer = ({ file, pdfUrl, numPages, pageNumber, setPageNumber, onFileChange, mode, crop, setCrop, setCompletedCrop, loading }) => {
  return (
    <div className="w-[40%] border-r border-gray-800 flex flex-col bg-[#0f121b]">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-[#131620]">
        <h2 className="font-semibold text-blue-400 flex items-center gap-2">
          <FileText size={18} /> Document Viewer
        </h2>
        <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-xs px-3 py-1.5 rounded-full flex items-center gap-2 transition hover:scale-105">
          {loading ? <Loader2 className="animate-spin" size={14}/> : <UploadCloud size={14} />} 
          Upload PDF
          <input type="file" hidden accept=".pdf" onChange={onFileChange} />
        </label>
      </div>

      {/* PDF Render Area */}
      <div className="flex-1 overflow-auto p-4 flex justify-center bg-gray-900/50 relative">
        {pdfUrl ? (
          <div className="shadow-2xl border border-gray-700">
            {mode === 'crop' ? (
              <ReactCrop crop={crop} onChange={(c) => setCrop(c)} onComplete={(c) => setCompletedCrop(c)}>
                <Document file={pdfUrl}>
                  <Page pageNumber={pageNumber} width={450} renderTextLayer={false} renderAnnotationLayer={false} />
                </Document>
              </ReactCrop>
            ) : (
              <Document file={pdfUrl}>
                <Page pageNumber={pageNumber} width={450} renderTextLayer={false} renderAnnotationLayer={false} />
              </Document>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-2 opacity-50">
            <FileText size={48} />
            <p>Upload a PDF to view content</p>
          </div>
        )}
      </div>

      {/* Footer / Controls */}
      {numPages && (
        <div className="p-3 bg-[#131620] border-t border-gray-800 flex justify-center items-center gap-4">
          <button disabled={pageNumber <= 1} onClick={() => setPageNumber((p) => p - 1)} className="p-1 hover:bg-gray-700 rounded disabled:opacity-30">
            <ChevronLeft />
          </button>
          <span className="text-sm font-mono text-gray-300">
            Page {pageNumber} of {numPages}
          </span>
          <button disabled={pageNumber >= numPages} onClick={() => setPageNumber((p) => p + 1)} className="p-1 hover:bg-gray-700 rounded disabled:opacity-30">
            <ChevronRight />
          </button>
        </div>
      )}
    </div>
  );
};

export default PDFViewer;
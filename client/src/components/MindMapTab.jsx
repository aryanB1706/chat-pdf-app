import React from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import { Loader2, BrainCircuit } from "lucide-react";
import 'reactflow/dist/style.css';

const MindMapTab = ({ mindMapNodes, mindMapEdges, generateMindMap, loading }) => {
  return (
    <div className="h-full relative bg-[#1a1f2e]">
      {mindMapNodes.length === 0 ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
          <div className="bg-purple-900/20 p-6 rounded-full mb-6">
             <BrainCircuit size={64} className="text-purple-400"/>
          </div>
          <h3 className="text-2xl font-bold text-gray-300 mb-2">Visualize Concepts</h3>
          <p className="text-gray-500 mb-8 max-w-sm">Turn boring text into interactive flowcharts and mind maps.</p>
          <button onClick={generateMindMap} disabled={loading} className="bg-purple-600 px-8 py-3 rounded-xl font-bold hover:bg-purple-500 flex items-center gap-2 shadow-lg shadow-purple-900/20 transition-all hover:scale-105">
            {loading ? <Loader2 className="animate-spin" /> : <BrainCircuit />} Create Mind Map
          </button>
        </div>
      ) : (
        <ReactFlow nodes={mindMapNodes} edges={mindMapEdges} fitView className="bg-gray-900">
          <Background color="#374151" gap={20} />
          <Controls className="bg-gray-800 border-gray-700 fill-white" />
        </ReactFlow>
      )}
    </div>
  );
};

export default MindMapTab;
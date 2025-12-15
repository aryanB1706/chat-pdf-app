import React from "react";
import { Loader2, Sparkles } from "lucide-react";

const QuizTab = ({ quizData, quizAnswers, setQuizAnswers, generateQuiz, loading }) => {
  return (
    <div className="h-full overflow-y-auto p-8 scrollbar-thin">
      {!quizData ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <h3 className="text-2xl font-bold text-gray-300 mb-4">Test your knowledge</h3>
          <p className="text-gray-500 mb-8 max-w-md">Generate an AI-powered quiz based on your PDF content to prepare for exams.</p>
          <button onClick={generateQuiz} disabled={loading} className="bg-blue-600 px-8 py-4 rounded-xl font-bold hover:bg-blue-500 flex items-center gap-3 shadow-lg shadow-blue-900/20 transition-all hover:scale-105">
            {loading ? <Loader2 className="animate-spin" /> : <Sparkles />} Generate Quiz
          </button>
        </div>
      ) : (
        <div className="space-y-8 max-w-3xl mx-auto">
          <div className="flex justify-between items-center border-b border-gray-800 pb-4">
            <h3 className="text-2xl font-bold text-blue-400">AI Generated Quiz</h3>
            <button onClick={generateQuiz} className="text-sm text-gray-400 hover:text-white underline">Regenerate New</button>
          </div>
          
          {quizData.map((q, qIndex) => (
            <div key={qIndex} className="bg-[#131620] p-6 rounded-2xl border border-gray-800 shadow-sm">
              <p className="font-semibold text-lg mb-6 flex gap-3">
                <span className="text-blue-500">Q{qIndex + 1}.</span> {q.question}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {q.options.map((opt, oIndex) => (
                  <button
                    key={oIndex}
                    onClick={() => setQuizAnswers((prev) => ({ ...prev, [qIndex]: oIndex }))}
                    className={`text-left p-4 rounded-xl border transition-all duration-200 ${
                      quizAnswers[qIndex] === oIndex
                        ? oIndex === q.answer
                          ? 'bg-green-500/10 border-green-500 text-green-400'
                          : 'bg-red-500/10 border-red-500 text-red-400'
                        : 'bg-gray-900 border-gray-700 hover:border-gray-500 text-gray-300'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
              {quizAnswers[qIndex] !== undefined && (
                <div className="mt-4 text-sm bg-gray-900/80 p-4 rounded-lg border-l-4 border-blue-500">
                  <span className="font-bold text-blue-400">Explanation: </span> {q.explanation}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default QuizTab;
"use client";

import { useState, useRef, useEffect } from "react";
import { Upload } from "@/components/Upload";
import { CodeViewer } from "@/components/CodeViewer";
import { Rocket, Laptop, CheckCircle2, Circle, Loader2 } from "lucide-react";

export default function Home() {
  const [status, setStatus] = useState<"idle" | "processing" | "complete" | "error">("idle");
  const [currentStep, setCurrentStep] = useState<string>("");
  const [logs, setLogs] = useState<string[]>([]);
  const [generatedCode, setGeneratedCode] = useState<string>("");
  const [framework, setFramework] = useState("react");

  const ws = useRef<WebSocket | null>(null);

  const steps = [
    { key: "preprocessing", label: "Preprocessing" },
    { key: "detection", label: "Detecting UI Elements" },
    { key: "ocr", label: "Extracting Text" },
    { key: "layout", label: "Analyzing Layout" },
    { key: "generation", label: "Generating Code" },
  ];

  const handleUpload = async (file: File) => {
    setStatus("processing");
    setLogs([]);
    setGeneratedCode("");
    setCurrentStep("preprocessing");

    // Convert file to base64
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      connectAndSend(base64);
    };
    reader.readAsDataURL(file);
  };

  const connectAndSend = (data: string) => {
    if (ws.current) {
      ws.current.close();
    }

    ws.current = new WebSocket("ws://localhost:8000/ws/generate");

    ws.current.onopen = () => {
      console.log("Connected to backend");
      // Send JSON payload
      ws.current?.send(JSON.stringify({
        image: data,
        framework: framework
      }));
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === "status") {
        setCurrentStep(message.step);
        setLogs((prev) => [...prev, message.message]);
      } else if (message.type === "code_chunk") {
        setGeneratedCode((prev) => prev + message.chunk);
      } else if (message.type === "complete") {
        setStatus("complete");
        setCurrentStep("complete");
        ws.current?.close();
      } else if (message.type === "error") {
        setStatus("error");
        setLogs((prev) => [...prev, `Error: ${message.message}`]);
        alert(message.message);
      }
    };

    ws.current.onerror = (e) => {
      console.error("WebSocket error", e);
      setStatus("error");
      setLogs((prev) => [...prev, "Connection error. Ensure backend is running."]);
    };
  };

  // Clean up code (remove markdown blocks)
  const cleanCode = (code: string) => {
    return code.replace(/^```(jsx|tsx|javascript|react|html)?/g, "").replace(/```$/g, "").trim();
  };

  const finalCode = cleanCode(generatedCode);

  const handleDownload = () => {
    const blob = new Blob([finalCode], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = framework === "html" ? "index.html" : "App.jsx";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const resetState = () => {
    setStatus("idle");
    setLogs([]);
    setGeneratedCode("");
    setCurrentStep("");
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl text-indigo-600">
            <Rocket className="w-6 h-6" />
            <span>Screenshot2Code</span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              disabled={status !== "idle"}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            >
              <option value="react">React (Tailwind)</option>
              <option value="html">HTML (Tailwind)</option>
            </select>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {(status === "idle") ? (
          <div className="max-w-2xl mx-auto mt-12 flex flex-col gap-12 animate-in fade-in zoom-in duration-500">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900">
                Turn Screenshots into <span className="text-indigo-600">React Code</span>
              </h1>
              <p className="text-lg text-gray-600 max-w-lg mx-auto">
                Upload a screenshot of any UI and let our AI pipeline detect elements, extract info, and generate clean code instantly.
              </p>
            </div>

            <div className="bg-white p-2 rounded-xl shadow-xl border border-gray-100">
              <Upload onUpload={handleUpload} isProcessing={false} />
            </div>
          </div>
        ) : (
          <div className="h-[calc(100vh-140px)] flex flex-col gap-4">
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border shadow-sm">
              <button
                onClick={resetState}
                className="text-sm font-medium text-gray-500 hover:text-gray-900 flex items-center gap-2 transition-colors"
              >
                ← Upload New Image
              </button>

              <div className="flex items-center gap-4">
                {/* Progress Stepper */}
                <div className="flex items-center gap-2 text-xs">
                  {steps.map((s, i) => {
                    const isActive = currentStep === s.key;
                    const isPast = steps.findIndex(x => x.key === currentStep) > i || status === "complete";
                    return (
                      <div key={s.key} className={`flex items-center gap-1 ${isActive ? 'text-indigo-600 font-bold' : isPast ? 'text-green-600' : 'text-gray-400'}`}>
                        {isActive && <Loader2 className="w-3 h-3 animate-spin" />}
                        {isPast && <CheckCircle2 className="w-3 h-3" />}
                        {!isActive && !isPast && <Circle className="w-3 h-3" />}
                        {s.label}
                        {i < steps.length - 1 && <span className="text-gray-300 mx-1">→</span>}
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  disabled={!finalCode}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors shadow-md ${finalCode
                    ? "bg-indigo-600 hover:bg-indigo-700 text-white"
                    : "bg-gray-300 text-gray-500 cursor-not-allowed"
                    }`}
                >
                  Download Code
                </button>
              </div>
            </div>

            <div className="h-full">
              <CodeViewer code={finalCode} language={framework} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

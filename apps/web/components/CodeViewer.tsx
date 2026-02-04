"use client";

import Editor from "@monaco-editor/react";

interface CodeViewerProps {
    code: string;
    language: string;
}

export function CodeViewer({ code, language }: CodeViewerProps) {
    return (
        <div className="h-full border rounded-lg overflow-hidden flex flex-col bg-[#1e1e1e]">
            <div className="bg-[#2d2d2d] px-4 py-2 text-xs text-gray-400 flex justify-between items-center border-b border-[#3e3e3e]">
                <span className="uppercase">{language}</span>
                <span>Read-only</span>
            </div>
            <div className="flex-1">
                <Editor
                    height="100%"
                    defaultLanguage={language}
                    value={code}
                    theme="vs-dark"
                    options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                        scrollBeyondLastLine: false,
                    }}
                />
            </div>
        </div>
    );
}

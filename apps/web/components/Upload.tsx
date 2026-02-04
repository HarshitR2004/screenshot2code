"use client";

import { Upload as UploadIcon, FileJson, Loader2 } from "lucide-react";
import { useCallback, useState } from "react";

interface UploadProps {
  onUpload: (file: File) => void;
  isProcessing: boolean;
}

export function Upload({ onUpload, isProcessing }: UploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0 && files[0].type.startsWith("image/")) {
        onUpload(files[0]);
      }
    },
    [onUpload]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0) {
        onUpload(files[0]);
      }
    },
    [onUpload]
  );

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
        isDragOver
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-gray-400"
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <label className="cursor-pointer block">
        <input
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleChange}
          disabled={isProcessing}
        />
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-gray-100 rounded-full">
            {isProcessing ? (
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            ) : (
              <UploadIcon className="w-8 h-8 text-gray-500" />
            )}
          </div>
          <div>
            <p className="text-lg font-medium">
              {isProcessing ? "Processing Screenshot..." : "Upload a Screenshot"}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Drag & drop or click to browse
            </p>
          </div>
        </div>
      </label>
    </div>
  );
}

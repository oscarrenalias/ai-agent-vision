import React, { useRef, useState } from "react";
import { InputProps, CopilotChat } from "@copilotkit/react-ui";
import { AgentStateProvider, useAgentState } from "../AgentStateProvider";

export function CustomInput({ inProgress, onSend, isVisible }: InputProps) {
  const [selectedFileName, setSelectedFileName] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { getAgentState, setAgentState } = useAgentState();

  const handleSubmit = async (value: string) => {
    if (!value.trim()) return;
    // If a file is selected, upload it first
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile);
      try {
        const res = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.status === "success") {
          //await onSend(`${value} [uploaded file: ${data.filename}]`);

          // update state
          setAgentState({
            ...getAgentState(),
            receipt_image_path: data.filename,
          });
          console.log("File uploaded. Agent state: ", getAgentState());
        } else {
          alert("(1) File upload failed: " + (data.error || "Unknown error"));
          return;
        }
      } catch (err) {
        alert("(2) File upload failed: " + err);
        return;
      }

      setSelectedFile(null);
      setSelectedFileName("");
    } else {
      onSend(value);
    }
  };

  const wrapperStyle = "flex gap-2 p-4 border-t";
  const inputStyle =
    "flex-1 p-2 rounded-md border border-gray-300 focus:outline-none focus:border-blue-500 disabled:bg-gray-100";
  const askButtonStyle =
    "px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed";
  const uploadButtonStyle =
    "px-4 py-2 bg-green-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed";

  return (
    <div className={wrapperStyle}>
      <input
        disabled={inProgress}
        type="text"
        placeholder="Ask your question here..."
        className={inputStyle}
        onKeyDown={async (e) => {
          if (e.key === "Enter") {
            await handleSubmit(e.currentTarget.value);
            e.currentTarget.value = "";
          }
        }}
      />
      <button
        disabled={inProgress}
        className={askButtonStyle}
        onClick={async (e) => {
          const input = e.currentTarget
            .previousElementSibling as HTMLInputElement;
          await handleSubmit(input.value);
          input.value = "";
        }}
        aria-label="Send"
      >
        <img src="/paperplane.svg" alt="Send" className="w-5 h-5" />
      </button>
      <input
        type="file"
        accept="image/*"
        style={{ display: "none" }}
        ref={fileInputRef}
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            setSelectedFileName(e.target.files[0].name);
            setSelectedFile(e.target.files[0]);
          }
        }}
      />
      <button
        disabled={inProgress}
        className={uploadButtonStyle}
        onClick={() => fileInputRef.current?.click()}
        aria-label="Attach file"
      >
        <img src="/paperclip.svg" alt="Attach file" className="w-5 h-5" />
      </button>
      {selectedFileName && (
        <span className="ml-2 text-xs text-gray-500">
          Selected: {selectedFileName}
        </span>
      )}
    </div>
  );
}

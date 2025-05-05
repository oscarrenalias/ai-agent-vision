import React, { createContext, useContext, useState, useEffect } from "react";
import { useCoAgent, useLangGraphInterrupt } from "@copilotkit/react-core";
import { AGENT_NAME, AgentState } from "../lib/types";
import AgentStateInspector from "./debug/AgentStateInspector";

type AgentStateContextType = {
  setAgentState: (newState: AgentState) => void;
  getAgentState: () => AgentState;
};

const AgentStateContext = createContext<AgentStateContextType | undefined>(
  undefined
);

export const AgentStateProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { state, setState } = useCoAgent<AgentState>({
    name: AGENT_NAME,
    initialState: {
      last_receipt: "",
      last_meal_plan: "",
      last_shopping_list: "",
      receipt_image_path: "",
    },
  });

  useLangGraphInterrupt({
    render: ({ event, resolve }) => {
      const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
      const [uploading, setUploading] = React.useState(false);
      const [error, setError] = React.useState<string | null>(null);
      const fileInputRef = React.useRef<HTMLInputElement>(null);

      const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
          setSelectedFile(e.target.files[0]);
          setError(null);
        }
      };

      const handleUpload = async () => {
        if (!selectedFile) return;
        setUploading(true);
        setError(null);
        try {
          const formData = new FormData();
          formData.append("file", selectedFile);
          const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
          });
          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }
          const data = await response.json();
          if (!data.id) {
            throw new Error("No file id returned from server");
          }
          resolve(data.id);
        } catch (err: any) {
          setError(err.message || "Unknown error");
          //resolve(`Error: ${err.message || "Unknown error"}`);
        } finally {
          //setUploading(false);
        }
      };

      return (
        <div className="upload-interrupt-box w-full max-w-none">
          <p className="upload-interrupt-title">{event.value}</p>
          <div className={uploading ? "hidden" : "upload-interrupt-row"}>
            <input
              type="file"
              accept=".jpg,.jpeg,.png"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="upload-interrupt-select"
            >
              Select Image
            </button>
            {selectedFile && (
              <span className="upload-interrupt-filename">
                {selectedFile.name}
              </span>
            )}
          </div>
          <div className={uploading ? "hidden" : "upload-interrupt-upload-row"}>
            <button
              type="button"
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="upload-interrupt-upload"
            >
              Upload
            </button>
          </div>
          {error && <div className="upload-interrupt-error">{error}</div>}
          {uploading && !error && (
            <div className="upload-interrupt-spinner-overlay">
              <div className="upload-interrupt-spinner-box">
                <span className="upload-interrupt-spinner" />
                <span className="upload-interrupt-spinner-text">
                  Uploading...
                </span>
              </div>
            </div>
          )}
        </div>
      );
    },
  });

  /*useEffect(() => {
    console.log("AgentStateProvider status changed:", state);
  }, [state]);*/

  const setAgentState = (newState: AgentState) => {
    setState((prevState) => {
      console.log("Previous state:", prevState);
      console.log("New state to merge:", newState);
      const merged = { ...prevState, ...newState };
      console.log("Merged state:", merged);
      return merged;
    });
  };

  const getAgentState = () => {
    return state;
  };

  return (
    <AgentStateContext.Provider value={{ setAgentState, getAgentState }}>
      <AgentStateInspector state={state} />
      {children}
    </AgentStateContext.Provider>
  );
};

export function useAgentState() {
  const ctx = useContext(AgentStateContext);
  if (!ctx)
    throw new Error("useAgentState must be used within AgentStateProvider");
  return ctx;
}

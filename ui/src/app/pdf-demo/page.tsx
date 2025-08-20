"use client";

import React, { useRef, useState } from "react";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import AttachFileIcon from "@mui/icons-material/AttachFile";

export default function PdfDemoPage() {
  const [selectedFileName, setSelectedFileName] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const fileInputRefUploadCard = useRef<HTMLInputElement>(null);

  const handleFileChangeCustomInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFileName(e.target.files[0].name);
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleFileChangeUploadCard = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFileName(e.target.files[0].name);
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <Box sx={{ padding: 4, maxWidth: 800, margin: '0 auto' }}>
      <Typography variant="h3" gutterBottom>
        PDF Upload Support Demo
      </Typography>
      
      <Typography variant="body1" paragraph>
        This page demonstrates the PDF file upload support that has been added to the AI Agent Vision application.
        The file inputs below now accept both images (.jpg, .jpeg, .png) and PDF files (.pdf).
      </Typography>

      <Card sx={{ marginBottom: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            CustomInput Component Style
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This is similar to the CustomInput component used in the copilotkit integration.
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, marginBottom: 2 }}>
            <input
              type="file"
              accept="image/*,.pdf"
              style={{ display: "none" }}
              ref={fileInputRef}
              onChange={handleFileChangeCustomInput}
            />
            <Button
              variant="contained"
              color="success"
              startIcon={<AttachFileIcon />}
              onClick={() => fileInputRef.current?.click()}
            >
              Attach File (Images + PDFs)
            </Button>
            {selectedFileName && (
              <Typography variant="body2" color="text.secondary">
                Selected: {selectedFileName}
              </Typography>
            )}
          </Box>
          
          {selectedFile && (
            <Box sx={{ padding: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="subtitle2">File Details:</Typography>
              <Typography variant="body2">Name: {selectedFile.name}</Typography>
              <Typography variant="body2">Size: {(selectedFile.size / 1024).toFixed(2)} KB</Typography>
              <Typography variant="body2">Type: {selectedFile.type}</Typography>
              <Typography variant="body2">
                File Extension: {selectedFile.name.split('.').pop()?.toUpperCase()}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      <Card sx={{ marginBottom: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            UploadCard Component Style
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This is similar to the UploadCard component used in receipt processing interrupts.
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, marginBottom: 2 }}>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              style={{ display: "none" }}
              ref={fileInputRefUploadCard}
              onChange={handleFileChangeUploadCard}
            />
            <Button
              variant="contained"
              color="primary"
              startIcon={<AttachFileIcon />}
              onClick={() => fileInputRefUploadCard.current?.click()}
            >
              Select File
            </Button>
            {selectedFileName && (
              <Typography variant="body2" color="text.secondary">
                {selectedFileName}
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Backend Support
          </Typography>
          <Typography variant="body2" paragraph>
            The backend has been updated to:
          </Typography>
          <ul>
            <li>
              <Typography variant="body2">
                Accept PDF files in addition to image files in the upload endpoint
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Automatically detect file type based on extension (PDF, JPEG, PNG, etc.)
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Use the correct MIME type when sending files to OpenAI&apos;s API:
                <ul>
                  <li><code>application/pdf</code> for PDF files</li>
                  <li><code>image/jpeg</code> for JPEG files</li>
                  <li><code>image/png</code> for PNG files</li>
                </ul>
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Process both images and PDFs through OpenAI&apos;s GPT-4o vision API for receipt analysis
              </Typography>
            </li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
}
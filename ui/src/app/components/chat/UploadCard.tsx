import React from "react";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";
import UploadIcon from "@mui/icons-material/Upload";
import CancelIcon from "@mui/icons-material/Cancel";
import ImageIcon from "@mui/icons-material/Image";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Box from "@mui/material/Box";

export default function UploadCard({
  event,
  resolve,
}: {
  event: any;
  resolve: (value: any) => void;
}) {
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
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card
      sx={{
        width: "100%",
        borderRadius: 3,
        boxShadow: 3,
        position: "relative",
      }}
    >
      <CardContent>
        <Typography
          variant="h6"
          className="upload-interrupt-title"
          gutterBottom
        >
          {event.value}
        </Typography>
        {uploading && !error && (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              py: 4,
            }}
          >
            <CircularProgress color="primary" />
            <Typography variant="body2" sx={{ mt: 2 }}>
              Uploading...
            </Typography>
          </Box>
        )}
        {!uploading && (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                style={{ display: "none" }}
                ref={fileInputRef}
                onChange={handleFileChange}
              />
              <Button
                variant="contained"
                color="primary"
                startIcon={<ImageIcon />}
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                sx={{ minWidth: 120, mr: 1 }}
              >
                Select File
              </Button>
              {selectedFile && (
                <Typography variant="body2" color="text.secondary">
                  {selectedFile.name}
                </Typography>
              )}
            </div>
            <CardActions
              sx={{ gap: 2, justifyContent: "flex-end", px: 0, mt: 2 }}
            >
              <Button
                variant="contained"
                color="success"
                startIcon={<UploadIcon />}
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                sx={{ minWidth: 120, mr: 1 }}
              >
                Upload
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<CancelIcon />}
                onClick={() => resolve("__CANCEL__")}
                disabled={uploading}
                sx={{ minWidth: 120, ml: 1 }}
              >
                Cancel
              </Button>
            </CardActions>
          </>
        )}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}

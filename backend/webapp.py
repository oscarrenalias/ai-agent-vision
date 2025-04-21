import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "webapp.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info",
        timeout_keep_alive=300,  # Keep-alive timeout in seconds
    )

import debugpy
import uvicorn

def main():
    # Enable debugging on port 5678
    debugpy.listen(("0.0.0.0", 5678))
    
    # Uncomment the following line to pause the script until a debugger attaches
    # debugpy.wait_for_client()
    
    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )

if __name__ == "__main__":
    main()

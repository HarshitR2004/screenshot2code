import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
import traceback

from fastapi.middleware.cors import CORSMiddleware

# Import our pipeline
from pipeline import ScreenshotPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScreenshotConverter")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline (Global singleton to avoid reloading models)
pipeline = None

@app.on_event("startup")
async def startup_event():
    global pipeline
    logger.info("Initializing Screenshot Pipeline...")
    pipeline = ScreenshotPipeline()
    logger.info("Pipeline initialized.")

@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected")
    
    try:
        while True:
            # Receive data (JSON expected with image and framework)
            message = await websocket.receive_text()
            
            # Default values
            image_data = message
            framework = "react"
            
            # Try parsing as JSON
            try:
                import json
                payload = json.loads(message)
                if isinstance(payload, dict):
                    image_data = payload.get("image", message)
                    framework = payload.get("framework", "react")
            except:
                pass
            
            # Run the 7-step pipeline
            if pipeline:
                async for status_update in pipeline.process(image_data, framework):
                    await websocket.send_json(status_update)
            else:
                await websocket.send_json({"status": "error", "message": "Pipeline not initialized"})
            
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        await websocket.send_json({"status": "error", "message": str(e)})

@app.post("/api/convert")
async def convert_image(
    file: UploadFile = File(...),
    framework: str = Form("react")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        content = await file.read()
        
        import base64
        b64_content = base64.b64encode(content).decode('utf-8')
        
        generated_code = ""
        layout = {}
        
        if pipeline:
            async for update in pipeline.process(b64_content, framework):
                if update["type"] == "code_chunk":
                    generated_code += update["chunk"]
                elif update["type"] == "complete":
                    pass
        
        return {
            "code": generated_code,
            "framework": framework
        }
    except Exception as e:
        logger.error(f"Error in HTTP convert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

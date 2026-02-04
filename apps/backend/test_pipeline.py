import asyncio
import cv2
import numpy as np
import base64
try:
    from apps.codegen_engine.pipeline import ScreenshotPipeline
except ImportError:
    from pipeline import ScreenshotPipeline

# Simple mock image (black square with a white rectangle)
def create_mock_image():
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (450, 150), (255, 255, 255), -1) # "Header"
    cv2.putText(img, "Login", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    _, buffer = cv2.imencode('.png', img)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

async def test_pipeline():
    print("Initializing Pipeline...")
    # mocking generator to avoid loading large model in test
    pipeline = ScreenshotPipeline()
    pipeline.generator.model = "MockModel" # Bypass real load if it takes too long, or let it load
    
    # Mocking generate_code_stream to avoid actual inference if model not present
    async def mock_stream(layout):
        yield "import React from 'react';\n"
        yield "export default function MockComponent() {\n"
        yield "  return <div>Mocked Code</div>;\n"
        yield "}\n"
    
    # We monkeypatch if model failed to load or just for speed
    if not pipeline.generator.model:
        pipeline.generator.generate_code_stream = mock_stream

    print("Pipeline Initialized. Processing mock image...")
    image_data = create_mock_image()
    
    async for update in pipeline.process(image_data):
        print(f"Update: {update['type']}")
        if update['type'] == 'code_chunk':
            print(f"Chunk: {update['chunk']}", end="")
            
    print("\nTest Complete.")

if __name__ == "__main__":
    try:
        import sys
        import os
        sys.path.append(os.getcwd())
        asyncio.run(test_pipeline())
    except ImportError:
        print("Please run this script from the project root: python apps/codegen-engine/test_pipeline.py")

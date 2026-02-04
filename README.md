# Screenshot to Code Converter

A tool to convert UI screenshots into working HTML/Tailwind or React code using local AI models.

## Features

- **Local Processing**: Uses local models via Ollama (no external API keys required).
- **Computer Vision**: OpenCV and EasyOCR for element detection and text extraction.
- **Code Generation**: Supports generating React (Tailwind) and HTML (Tailwind) code.
- **Download**: Export generated code as .jsx or .html files.

## Prerequisites

- **Node.js**: Version 18 or higher.
- **Python**: Version 3.10 or higher.
- **Ollama**: Must be installed and running locally.
  - Recommended Model: `gemma3n:e4b` (or update `apps/backend/engine/generator.py` with your preferred model).

## Installation and Setup

### 1. Backend Setup

Navigate to the backend directory:

```bash
cd apps
```

Install Python dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI server:

```bash
python backend/main.py
```

The backend API will run on `http://localhost:8000`.

### 2. Frontend Setup

Navigate to the web directory:

```bash
cd apps/web
```

Install Node.js dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend application will be available at `http://localhost:3000`.

## Usage

1. Ensure Ollama is running (`ollama serve`).
2. Start both the backend and frontend servers.
3. Open `http://localhost:3000` in your browser.
4. Upload a screenshot of a user interface.
5. Wait for the pipeline to process the image (Detection -> OCR -> Layout -> Code Generation).
6. View the generated code and the live preview.
7. Download the result.

## Architecture

The system uses a multi-step pipeline approach:
1. **Preprocessing**: Image optimization.
2. **Detection**: Identifying UI elements using computer vision techniques.
3. **OCR**: Extracting text content from the image.
4. **Layout Analysis**: Structuring detected elements into a hierarchy.
5. **Code Generation**: Using a Large Language Model (LLM) to convert the layout into code.

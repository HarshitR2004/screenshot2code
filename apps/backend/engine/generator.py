import logging
import json
import requests

logger = logging.getLogger("ScreenshotConverter")

class CodeGenerator:
    def __init__(self, model_id="gemma3n:e4b"):
        self.model_id = model_id
        self.api_url = "http://localhost:11434/api/chat"
        logger.info(f"Initialized CodeGenerator with Ollama model: {self.model_id}")

    async def generate_code_stream(self, layout_tree, framework="react"):
        """
        Generates code from the layout tree using the Ollama LLM.
        Yields chunks of generated code.
        """
        # 1. Construct Prompt
        # Flatten tree to string for the prompt
        layout_str = json.dumps(layout_tree, indent=2)
        
        if framework == "html":
            system_prompt = """You are an expert Frontend Developer specializing in HTML and Tailwind CSS.
You will be provided with a JSON representation of a UI layout.
Your task is to generate a single, valid HTML file that implements this layout.
- Use Tailwind CSS via CDN (<script src="https://cdn.tailwindcss.com"></script>).
- Use FontAwesome or SVG for icons if needed (e.g., <link ... font-awesome>).
- Ensure the code is self-contained in a single <html> file.
- Do not wrap the code in markdown blocks (```). Just output the raw HTML code.
"""
            user_prompt = f"""Generate HTML+Tailwind Code for the following Layout:
{layout_str}
"""
        else:
            # Default to React
            system_prompt = """You are an expert Frontend Developer specializing in React and Tailwind CSS.
You will be provided with a JSON representation of a UI layout.
Your task is to generate valid, modern React code that implements this layout.
- Use functional components.
- Use Tailwind CSS for styling.
- Use the 'lucide-react' library for icons if mentioned in text (e.g., 'Settings', 'Menu').
- Ensure the code is self-contained and runnable.
- Do not wrap the code in markdown blocks (```). Just output the code.
"""
            user_prompt = f"""Generate React Code for the following Layout:
{layout_str}
"""

        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            logger.info("Sending request to Ollama...")
            # Connect to Ollama
            # Note: We use requests (synchronous) here. In a high-concurrency async app, 
            # this should be `httpx` or run in an executor, but for this local tool it is fine.
            with requests.post(self.api_url, json=payload, stream=True) as response:
                if response.status_code != 200:
                    error_msg = f"// Error: Ollama returned status {response.status_code}\n// {response.text}\n"
                    logger.error(error_msg)
                    yield error_msg
                    return

                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if "message" in json_response:
                                content = json_response["message"].get("content", "")
                                if content:
                                    yield content
                            if json_response.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
            logger.info("Ollama generation complete.")
                            
        except requests.exceptions.ConnectionError:
            msg = "// Error: Could not connect to Ollama. Is it running at http://localhost:11434?\n"
            logger.error(msg)
            yield msg
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            yield f"// Error generating code: {e}\n"

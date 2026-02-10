import json
import httpx
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Configure logger
logger = logging.getLogger(__name__)

class OllamaClientError(Exception):
    """Base exception for Ollama client errors."""
    pass

class OllamaConnectionError(OllamaClientError):
    """Failed to connect to Ollama."""
    pass

class OllamaGenerationError(OllamaClientError):
    """Error during generation."""
    pass

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.Client(base_url=base_url, timeout=timeout)

    def health_check(self) -> bool:
        """Checks if Ollama instance is reachable."""
        try:
            response = self.client.get("/")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def generate(self, prompt: str, model: str, temperature: float = 0.7) -> str:
        """
        Generates text completion.
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaGenerationError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise OllamaGenerationError(f"Unexpected error: {e}")

    @retry(
        stop=stop_after_attempt(3), # 1 initial + 2 retries
        wait=wait_fixed(1),
        retry=retry_if_exception_type((json.JSONDecodeError, OllamaGenerationError)),
        reraise=True
    )
    def generate_json(self, prompt: str, model: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Generates structured JSON output. Retries if output is not valid JSON.
        """
        prompt_with_instruction = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON."
        
        try:
            payload = {
                "model": model,
                "prompt": prompt_with_instruction,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            raw_response = response.json().get("response", "")
            
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from Ollama: {raw_response[:100]}...")
                raise # Triggers retry
                
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaGenerationError(f"HTTP error {e.response.status_code}: {e.response.text}")

    def close(self):
        self.client.close()

import os

class LLMClient:
    def check_grammar(self, text):
        raise NotImplementedError

    def proofread(self, text):
        raise NotImplementedError

class MockLLMClient(LLMClient):
    def check_grammar(self, text):
        return f"ERROR: App is in MOCK MODE. API Key not loaded.\nPlease run with 'uv run main.py' or check .env file.\nOriginal text:\n{text}"

    def proofread(self, text):
        return "ERROR: App is in MOCK MODE. API Key not loaded."

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiClient(LLMClient):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        if not genai:
            raise ImportError("google-generativeai package not installed. Run 'uv sync'.")
        
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def check_grammar(self, text):
        prompt = f"Check the grammar of the following text and provide the CORRECTED version. Return ONLY the corrected text. Do not include explanations or bullet points.\n\n{text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def proofread(self, text):
        prompt = f"Proofread the following text and provide a corrected version. Maintain the original meaning and tone.\n\n{text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

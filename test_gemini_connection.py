import os
from dotenv import load_dotenv
from llm import GeminiClient

def test_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    print(f"Testing Gemini with key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        client = GeminiClient(api_key=api_key)
        text = "Me fail English? That's unpossible!"
        print(f"\nInput text: {text}")
        
        print("\nChecking grammar...")
        suggestions = client.check_grammar(text)
        print("Suggestions:")
        print(f"{suggestions}")
            
        print("\nProofreading...")
        proofread = client.proofread(text)
        print(f"Proofread version: {proofread}")
        
        print("\nSUCCESS: Gemini API is working!")
    except Exception as e:
        print(f"\nFAILURE: {str(e)}")

if __name__ == "__main__":
    test_gemini()

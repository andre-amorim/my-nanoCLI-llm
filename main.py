import curses
import sys
import argparse
from editor import Editor
from ui import CursesUI
from llm import MockLLMClient, GeminiClient
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_LOADED = True
except ImportError:
    DOTENV_LOADED = False

def main(stdscr, filename):
    curses.raw() # Capture all keys including ^O, ^C
    # Determine LLM Client
    llm_client = None
    
    # Check for Gemini first (Primary Strategy)
    if os.getenv("GEMINI_API_KEY"):
        try:
            llm_client = GeminiClient()
        except Exception:
            pass
            
    if not llm_client:
        llm_client = MockLLMClient()

    editor = Editor(filename, llm_client)
    
    # Set initial status
    if isinstance(llm_client, MockLLMClient):
        msg = "MOCK MODE."
        if os.path.exists(".env") and not DOTENV_LOADED:
            msg += " ERROR: .env found but python-dotenv missing! Try 'uv run python main.py'"
        else:
            msg += " Set GEMINI_API_KEY in .env to use Real LLM."
        editor.set_status(msg)
    elif isinstance(llm_client, GeminiClient):
        editor.set_status("Using Google Gemini.")

    ui = CursesUI(stdscr, editor)
    ui.run()

def entry_point():
    parser = argparse.ArgumentParser(description="Nano-like LLM Editor")
    parser.add_argument("filename", nargs="?", help="File to open")
    args = parser.parse_args()

    curses.wrapper(main, args.filename)

if __name__ == "__main__":
    entry_point()

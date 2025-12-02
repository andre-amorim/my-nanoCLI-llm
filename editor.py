import os

class Buffer:
    def __init__(self, filename=None):
        self.filename = filename
        self.lines = [""]
        self.cx = 0
        self.cy = 0
        self.scroll_y = 0
        self.modified = False
        if filename and os.path.exists(filename):
            self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.lines = f.read().splitlines()
                if not self.lines:
                    self.lines = [""]
        except Exception as e:
            # Handle new file or permission error gracefully
            pass

    def save(self):
        if not self.filename:
            return False, "No filename specified."
        try:
            with open(self.filename, 'w') as f:
                f.write("\n".join(self.lines))
            self.modified = False
            return True, "File Saved!"
        except Exception as e:
            return False, f"Error: {str(e)}"

class Editor:
    def __init__(self, filename=None, llm_client=None):
        self.buffer = Buffer(filename)
        self.llm_client = llm_client
        self.status_message = "" # Status is now just for messages, help is separate
        self.mode = "NORMAL" # NORMAL, INSERT (implicit in nano), etc.

    def set_status(self, message):
        self.status_message = message

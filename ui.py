import curses

class CursesUI:
    def __init__(self, stdscr, editor):
        self.stdscr = stdscr
        self.editor = editor
        self.height, self.width = stdscr.getmaxyx()
        self.running = True
        
        # Setup colors if possible
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Define some pairs
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status bar
        
        self.last_key = None

    def run(self):
        while self.running:
            self.update_dimensions()
            self.draw()
            self.handle_input()

    def update_dimensions(self):
        self.height, self.width = self.stdscr.getmaxyx()

    def draw(self):
        self.stdscr.clear()
        
        # Draw Title Bar
        provider = "UNKNOWN"
        client = self.editor.llm_client
        if "MockLLMClient" in str(type(client)):
            provider = "MOCK(No Key)"
        elif "GeminiClient" in str(type(client)):
            provider = "GEMINI"

        title = f" NanoLLM 0.1.0 | {provider} | {self.editor.buffer.filename or 'New Buffer'}"
        if self.editor.buffer.modified:
            title += " *"
        self.stdscr.addstr(0, 0, title.ljust(self.width), curses.color_pair(1))

        # Draw Text
        # Simple scrolling logic
        buf = self.editor.buffer
        
        # Available height for text: Total - TopBar(1) - StatusBar(1) - HelpMenu(2) = Total - 4
        text_height = self.height - 4
        
        # Ensure cursor is visible (scroll adjustment)
        if buf.cy < buf.scroll_y:
            buf.scroll_y = buf.cy
        if buf.cy >= buf.scroll_y + text_height:
            buf.scroll_y = buf.cy - text_height + 1

        for y in range(text_height):
            file_line_idx = buf.scroll_y + y
            if file_line_idx < len(buf.lines):
                line_content = buf.lines[file_line_idx]
                self.stdscr.addstr(y + 1, 0, line_content[:self.width])

        # Draw Status Bar (3rd line from bottom)
        status = self.editor.status_message
        try:
            if self.last_key is not None:
                status += f" | Key: {self.last_key}"
            self.stdscr.addstr(self.height - 3, 0, status.ljust(self.width), curses.color_pair(1))
        except curses.error:
            pass

        # Draw Help Menu (Bottom 2 lines)
        help_lines = [
            "^G Get Help  ^O Write Out  ^W Where Is  ^K Cut Text  ^J Justify  ^C Cur Pos",
            "^X Exit      ^R Read File  ^\\ Replace   ^U Uncut Text^T To Spell ^_ Go To Line"
        ]
        # Custom help for our app
        help_lines = [
            "^G Grammar   ^O Save      ^X Exit",
            "                                 "
        ]
        
        try:
            self.stdscr.addstr(self.height - 2, 0, help_lines[0].ljust(self.width), curses.color_pair(0))
            self.stdscr.addstr(self.height - 1, 0, help_lines[1].ljust(self.width), curses.color_pair(0))
        except curses.error:
            pass

        # Move Cursor
        # Calculate screen coordinates
        screen_y = buf.cy - buf.scroll_y + 1
        screen_x = buf.cx
        
        # Clamp cursor to screen
        # Text area ends at height - 4 (exclusive), so max y index is height - 4
        if 0 <= screen_y < self.height - 3 and 0 <= screen_x < self.width:
            try:
                self.stdscr.move(screen_y, screen_x)
            except curses.error:
                pass
        
        self.stdscr.refresh()

    def handle_input(self):
        try:
            key = self.stdscr.getch()
            self.last_key = key # Debugging
        except KeyboardInterrupt:
            self.running = False
            return

        # Handle Ctrl+X (Exit)
        if key == 24: # Ctrl+X
            if self.editor.buffer.modified:
                self.editor.set_status("Save modified buffer? (Y/N)")
                self.stdscr.refresh()
                while True:
                    try:
                        ch = self.stdscr.getch()
                        if ch in (ord('y'), ord('Y')):
                            success, msg = self.editor.buffer.save()
                            if success:
                                self.running = False
                                break
                            else:
                                self.editor.set_status(msg + " Press any key...")
                                self.stdscr.getch()
                                break
                        elif ch in (ord('n'), ord('N')):
                            self.running = False
                            break
                        elif ch == 3: # Ctrl+C to cancel
                            self.editor.set_status("Cancelled.")
                            break
                    except KeyboardInterrupt:
                        break
            else:
                self.running = False
        # Handle Ctrl+O (Save)
        elif key == 15: # Ctrl+O
            success, msg = self.editor.buffer.save()
            self.editor.set_status(msg)
        elif key == 3: # Ctrl+C
            msg = f"Line: {self.editor.buffer.cy + 1}/{len(self.editor.buffer.lines)} Col: {self.editor.buffer.cx + 1}"
            self.editor.set_status(msg)
        # Handle Ctrl+G (Grammar Check)
        elif key == 7: # Ctrl+G
            self.editor.set_status("Checking grammar...")
            self.stdscr.refresh()
            # Get full text
            text = "\n".join(self.editor.buffer.lines)
            try:
                corrected_text = self.editor.llm_client.check_grammar(text)
                if corrected_text and not corrected_text.startswith("Error:"):
                    # Replace buffer content
                    self.editor.buffer.lines = corrected_text.splitlines()
                    self.editor.buffer.modified = True
                    self.editor.set_status("Grammar checked and text updated.")
                else:
                    self.editor.set_status(f"LLM Error: {corrected_text}")
            except Exception as e:
                self.editor.set_status(f"LLM Error: {str(e)}")
        # Navigation
        elif key == curses.KEY_UP:
            self.editor.buffer.cy = max(0, self.editor.buffer.cy - 1)
        elif key == curses.KEY_DOWN:
            self.editor.buffer.cy = min(len(self.editor.buffer.lines) - 1, self.editor.buffer.cy + 1)
        elif key == curses.KEY_LEFT:
            self.editor.buffer.cx = max(0, self.editor.buffer.cx - 1)
        elif key == curses.KEY_RIGHT:
            # Allow moving past end of line? Nano usually does, but let's stick to line length for now
            line_len = len(self.editor.buffer.lines[self.editor.buffer.cy])
            self.editor.buffer.cx = min(line_len, self.editor.buffer.cx + 1)
        # Basic Typing (very simplified)
        elif 32 <= key <= 126:
            char = chr(key)
            line = self.editor.buffer.lines[self.editor.buffer.cy]
            cx = self.editor.buffer.cx
            self.editor.buffer.lines[self.editor.buffer.cy] = line[:cx] + char + line[cx:]
            self.editor.buffer.cx += 1
            self.editor.buffer.modified = True
        # Backspace
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            cx = self.editor.buffer.cx
            if cx > 0:
                line = self.editor.buffer.lines[self.editor.buffer.cy]
                self.editor.buffer.lines[self.editor.buffer.cy] = line[:cx-1] + line[cx:]
                self.editor.buffer.cx -= 1
                self.editor.buffer.modified = True
        # Enter
        elif key == 10: # Enter
            # Split line
            line = self.editor.buffer.lines[self.editor.buffer.cy]
            cx = self.editor.buffer.cx
            self.editor.buffer.lines[self.editor.buffer.cy] = line[:cx]
            self.editor.buffer.lines.insert(self.editor.buffer.cy + 1, line[cx:])
            self.editor.buffer.cy += 1
            self.editor.buffer.cx = 0
            self.editor.buffer.modified = True

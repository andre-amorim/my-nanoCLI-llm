import unittest
from unittest.mock import MagicMock
import sys
import os

# Mock curses before importing ui
mock_curses = MagicMock()
mock_curses.COLOR_BLACK = 0
mock_curses.COLOR_WHITE = 7
mock_curses.KEY_UP = 259
mock_curses.KEY_DOWN = 258
mock_curses.KEY_LEFT = 260
mock_curses.KEY_RIGHT = 261
mock_curses.KEY_BACKSPACE = 263
mock_curses.error = Exception
sys.modules['curses'] = mock_curses

# Now import ui
import ui

class TestCursesUI(unittest.TestCase):
    def setUp(self):
        self.stdscr = MagicMock()
        self.stdscr.getmaxyx.return_value = (24, 80) # Standard terminal size
        
        self.editor = MagicMock()
        self.editor.buffer = MagicMock()
        self.editor.buffer.lines = ["Hello World"]
        self.editor.buffer.cx = 0
        self.editor.buffer.cy = 0
        self.editor.buffer.scroll_y = 0
        self.editor.buffer.filename = "test.txt"
        self.editor.buffer.modified = False
        self.editor.llm_client = MagicMock()
        self.editor.status_message = "Ready"
        
        self.ui = ui.CursesUI(self.stdscr, self.editor)

    def test_draw_help_menu(self):
        self.ui.draw()
        
        # Verify help menu calls
        # We expect addstr to be called with the help strings
        # The help strings in ui.py are:
        # "^G Grammar   ^O Save      ^X Exit"
        
        # We can check all calls to addstr
        calls = self.stdscr.addstr.call_args_list
        
        # Flatten arguments to search for strings
        all_args = [arg for call in calls for arg in call[0] if isinstance(arg, str)]
        
        found = False
        for arg in all_args:
            if "^G Grammar   ^O Save      ^X Exit" in arg:
                found = True
                break
        
        self.assertTrue(found, f"Help menu line 1 not found in: {all_args}")
        
    def test_draw_status_bar(self):
        self.ui.draw()
        calls = self.stdscr.addstr.call_args_list
        all_args = [arg for call in calls for arg in call[0] if isinstance(arg, str)]
        
        found = False
        for arg in all_args:
            if "Ready" in arg:
                found = True
                break
                
        self.assertTrue(found, f"Status message 'Ready' not found in: {all_args}")

if __name__ == '__main__':
    unittest.main()

import unittest
import os
from editor import Editor, Buffer

class TestEditor(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_buffer_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_buffer_load(self):
        buf = Buffer(self.test_file)
        self.assertEqual(buf.lines, ["Line 1", "Line 2"])

    def test_buffer_save(self):
        buf = Buffer(self.test_file)
        buf.lines = ["Modified Line 1", "Line 2"]
        success, msg = buf.save()
        self.assertTrue(success)
        
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Modified Line 1\nLine 2")

    def test_editor_init(self):
        editor = Editor(self.test_file)
        self.assertEqual(editor.buffer.filename, self.test_file)
        self.assertEqual(editor.buffer.lines, ["Line 1", "Line 2"])

if __name__ == '__main__':
    unittest.main()

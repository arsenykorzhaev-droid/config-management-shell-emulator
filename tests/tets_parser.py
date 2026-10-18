import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import ShellEmulator, VFS, VFSNode


class TestParser(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator.__new__(ShellEmulator)

    def test_parse_simple(self):
        cmd, args = self.emulator.parse_command("ls -la")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, ["-la"])

    def test_parse_quotes(self):
        cmd, args = self.emulator.parse_command('ls "моя папка"')
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, ["моя папка"])

    def test_parse_empty(self):
        cmd, args = self.emulator.parse_command("")
        self.assertIsNone(cmd)
        self.assertEqual(args, [])


class TestVFS(unittest.TestCase):
    def test_empty_vfs(self):
        vfs = VFS("Test")
        self.assertEqual(vfs.name, "Test")
        self.assertTrue(vfs.root.is_dir)

    def test_add_child(self):
        vfs = VFS()
        node = VFSNode("test.txt", is_dir=False, content="hello")
        vfs.root.add_child(node)

        found = vfs.find_node("/test.txt")
        self.assertIsNotNone(found)
        self.assertEqual(found.content, "hello")

    def test_find_nested(self):
        vfs = VFS()
        d = VFSNode("dir", is_dir=True)
        vfs.root.add_child(d)
        f = VFSNode("file.txt", is_dir=False, content="hi")
        d.add_child(f)

        self.assertIsNotNone(vfs.find_node("/dir/file.txt"))
        self.assertIsNone(vfs.find_node("/nonexistent"))


if __name__ == "__main__":
    unittest.main()
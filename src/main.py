import tkinter as tk
from tkinter import scrolledtext
import os
import shlex
import argparse
import xml.etree.ElementTree as ET


class VFSNode:
    def __init__(self, name, is_dir=False, content=""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}

    def add_child(self, node):
        self.children[node.name] = node

    def get_child(self, name):
        return self.children.get(name)


class VFS:
    def __init__(self, name="MyVFS"):
        self.name = name
        self.root = VFSNode("/", is_dir=True)

    def load_from_xml(self, path):
        try:
            tree = ET.parse(path)
            root_xml = tree.getroot()

            if 'name' in root_xml.attrib:
                self.name = root_xml.attrib['name']

            self.root = VFSNode("/", is_dir=True)
            for child in root_xml:
                self._parse_node(child, self.root)

            return True, "OK"
        except FileNotFoundError:
            return False, f"Файл VFS не найден: {path}"
        except ET.ParseError as e:
            return False, f"Ошибка парсинга XML: {e}"
        except Exception as e:
            return False, f"Ошибка загрузки VFS: {e}"

    def _parse_node(self, xml_node, parent):
        node_name = xml_node.attrib.get('name', 'unnamed')

        if xml_node.tag == 'dir':
            dir_node = VFSNode(node_name, is_dir=True)
            parent.add_child(dir_node)
            for child in xml_node:
                self._parse_node(child, dir_node)
        elif xml_node.tag == 'file':
            content = xml_node.text or ""
            file_node = VFSNode(node_name, is_dir=False, content=content)
            parent.add_child(file_node)

    def find_node(self, path):
        if path == "/" or path == "":
            return self.root

        parts = [p for p in path.split("/") if p]
        current = self.root

        for part in parts:
            if not current.is_dir:
                return None
            current = current.get_child(part)
            if current is None:
                return None

        return current


class ShellEmulator:
    def __init__(self, root, vfs_name="MyVFS", vfs_path=None, script_path=None):
        self.root = root
        self.vfs_name = vfs_name
        self.vfs_path = vfs_path
        self.script_path = script_path

        self.vfs = VFS(vfs_name)
        self.current_dir = "/"
        self.history = []

        self.root.title(f"Эмулятор оболочки - {self.vfs_name}")
        self.root.geometry("800x600")

        self.output_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', font=("Consolas", 10)
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.prompt_label = tk.Label(
            self.input_frame, text="> ", font=("Consolas", 10)
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(
            self.input_frame, font=("Consolas", 10)
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.focus()

        self.print_to_output(f"Добро пожаловать в {self.vfs_name}!")

        if self.vfs_path:
            self.load_vfs(self.vfs_path)
        else:
            self.print_to_output("VFS по умолчанию (пустая).")

        self.print_to_output("Введите 'help' для списка команд.")

        if self.script_path:
            self.run_startup_script(self.script_path)

    def print_to_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def load_vfs(self, path):
        self.print_to_output(f"Загрузка VFS из: {path}")
        success, message = self.vfs.load_from_xml(path)
        if success:
            self.vfs_name = self.vfs.name
            self.print_to_output(f"VFS загружена: {self.vfs_name}")
            self.root.title(f"Эмулятор оболочки - {self.vfs_name}")
        else:
            self.print_to_output(f"Ошибка: {message}")

    def expand_env_vars(self, text):
        return os.path.expandvars(text)

    def parse_command(self, command_line):
        try:
            parts = shlex.split(command_line)
        except ValueError:
            return None, []
        if not parts:
            return None, []
        return parts[0], parts[1:]

    def run_startup_script(self, script_path):
        if not os.path.isfile(script_path):
            self.print_to_output(f"Ошибка: скрипт не найден: {script_path}")
            return

        self.print_to_output(f"Выполнение скрипта: {script_path}")

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.print_to_output(f"Ошибка чтения скрипта: {e}")
            return

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            self.print_to_output(f"> {stripped}")
            expanded = self.expand_env_vars(stripped)
            command, args = self.parse_command(expanded)

            if command is None:
                self.print_to_output(f"Ошибка: строка {line_number}.")
                continue

            self._execute_parsed_command(command, args)

        self.print_to_output("Скрипт завершён.")

    def execute_command(self, event):
        command_line = self.command_entry.get()
        self.command_entry.delete(0, tk.END)

        if not command_line.strip():
            return

        self.print_to_output(f"> {command_line}")

        expanded_line = self.expand_env_vars(command_line)
        command, args = self.parse_command(expanded_line)

        if command is None:
            self.print_to_output("Ошибка: не удалось разобрать команду.")
            return

        self._execute_parsed_command(command, args)

    def _execute_parsed_command(self, command, args):
        if command not in ("history", "exit"):
            self.history.append(f"{command} {' '.join(args)}".strip())

        if command == "exit":
            self.root.quit()
            self.root.destroy()
        elif command == "help":
            self.print_to_output("Команды: ls, cd, pwd, cat, rev, history, find, rm, help, exit")
        elif command == "pwd":
            self.print_to_output(self.current_dir)
        elif command == "ls":
            self._cmd_ls(args)
        elif command == "cd":
            self._cmd_cd(args)
        elif command == "cat":
            self._cmd_cat(args)
        elif command == "rev":
            self._cmd_rev(args)
        elif command == "history":
            self._cmd_history(args)
        elif command == "find":
            self._cmd_find(args)
        elif command == "rm":
            self._cmd_rm(args)
        else:
            self.print_to_output(f"Ошибка: команда '{command}' не найдена.")

    def _cmd_ls(self, args):
        if not args:
            path = self.current_dir
        elif len(args) == 1:
            path = args[0]
        else:
            self.print_to_output("Ошибка: 'ls' принимает максимум 1 аргумент.")
            return

        node = self._resolve_path(path)
        if node is None:
            self.print_to_output(f"Ошибка: путь не найден: {path}")
            return

        if not node.is_dir:
            self.print_to_output(node.name)
            return

        if not node.children:
            self.print_to_output("(пусто)")
            return

        for name, child in sorted(node.children.items()):
            suffix = "/" if child.is_dir else ""
            self.print_to_output(f" {name}{suffix}")

    def _cmd_cd(self, args):
        if len(args) > 1:
            self.print_to_output("Ошибка: 'cd' принимает максимум 1 аргумент.")
            return

        if not args:
            self.current_dir = "/"
            return

        path = args[0]
        node = self._resolve_path(path)

        if node is None:
            self.print_to_output(f"Ошибка: директория не найдена: {path}")
            return

        if not node.is_dir:
            self.print_to_output(f"Ошибка: не директория: {path}")
            return

        self.current_dir = self._normalize_path(path)

    def _cmd_cat(self, args):
        if len(args) != 1:
            self.print_to_output("Ошибка: 'cat' требует 1 аргумент.")
            return

        node = self._resolve_path(args[0])
        if node is None:
            self.print_to_output(f"Ошибка: файл не найден: {args[0]}")
            return

        if node.is_dir:
            self.print_to_output(f"Ошибка: '{args[0]}' — директория.")
            return

        self.print_to_output(node.content)

    def _cmd_rev(self, args):
        if len(args) != 1:
            self.print_to_output("Ошибка: 'rev' требует 1 аргумент.")
            return
        node = self._resolve_path(args[0])
        if node is None:
            self.print_to_output(f"Ошибка: файл не найден: {args[0]}")
            return
        if node.is_dir:
            self.print_to_output(f"Ошибка: '{args[0]}' — директория.")
            return
        lines = node.content.splitlines()
        for line in reversed(lines):
            self.print_to_output(line)

    def _cmd_history(self, args):
        if args:
            self.print_to_output("Ошибка: 'history' не принимает аргументов.")
            return
        if not self.history:
            self.print_to_output("(история пуста)")
            return
        for i, cmd in enumerate(self.history, start=1):
            self.print_to_output(f" {i} {cmd}")

    def _cmd_find(self, args):
        if len(args) != 1:
            self.print_to_output("Ошибка: 'find' требует 1 аргумент (имя).")
            return
        target = args[0]
        results = []
        self._find_recursive(self.vfs.root, "/", target, results)
        if not results:
            self.print_to_output(f"Не найдено: {target}")
        else:
            for path in results:
                self.print_to_output(path)

    def _find_recursive(self, node, current_path, target, results):
        for name, child in node.children.items():
            child_path = f"{current_path.rstrip('/')}/{name}"
            if name == target:
                results.append(child_path)
            if child.is_dir:
                self._find_recursive(child, child_path, target, results)

    def _cmd_rm(self, args):
        if len(args) != 1:
            self.print_to_output("Ошибка: 'rm' требует 1 аргумент (путь).")
            return

        path = self._normalize_path(args[0])

        if path == "/":
            self.print_to_output("Ошибка: нельзя удалить корень.")
            return

        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]

        parent = self.vfs.find_node(parent_path)
        if parent is None or not parent.is_dir:
            self.print_to_output(f"Ошибка: родительская директория не найдена: {parent_path}")
            return

        target = parent.get_child(name)
        if target is None:
            self.print_to_output(f"Ошибка: не найдено: {path}")
            return

        if target.is_dir and target.children:
            self.print_to_output(f"Ошибка: директория не пуста: {path}")
            return

        del parent.children[name]
        self.print_to_output(f"Удалено: {path}")

    def _resolve_path(self, path):
        abs_path = self._normalize_path(path)
        return self.vfs.find_node(abs_path)

    def _normalize_path(self, path):
        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
        else:
            base = [p for p in self.current_dir.split("/") if p]
            extra = [p for p in path.split("/") if p]
            parts = base + extra

        result = []
        for part in parts:
            if part == ".":
                continue
            elif part == "..":
                if result:
                    result.pop()
            else:
                result.append(part)

        return "/" + "/".join(result) if result else "/"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС — Этап 5"
    )
    parser.add_argument("--vfs-path", dest="vfs_path", type=str, default=None,
                        help="Путь к физическому расположению VFS (XML-файл)")
    parser.add_argument("--script", dest="script_path", type=str, default=None,
                        help="Путь к стартовому скрипту")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    root = tk.Tk()
    app = ShellEmulator(
        root, "MyVFS",
        vfs_path=args.vfs_path,
        script_path=args.script_path
    )
    root.mainloop()
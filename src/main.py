import tkinter as tk
from tkinter import scrolledtext
import os
import shlex
import argparse


class ShellEmulator:
    def __init__(self, root, vfs_name="MyVFS", vfs_path=None, script_path=None):
        self.root = root
        self.vfs_name = vfs_name
        self.vfs_path = vfs_path
        self.script_path = script_path

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
        self.print_to_output(f"VFS path: {self.vfs_path or '(не задан)'}")
        self.print_to_output(f"Script path: {self.script_path or '(не задан)'}")
        self.print_to_output("Введите 'help' для списка команд.")

        if self.script_path:
            self.run_startup_script(self.script_path)

    def print_to_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

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
                self.print_to_output(f"Ошибка: строка {line_number} — не удалось разобрать.")
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
        if command == "exit":
            if args:
                self.print_to_output("Ошибка: 'exit' не принимает аргументов.")
                return
            self.root.quit()
            self.root.destroy()

        elif command == "help":
            if args:
                self.print_to_output("Ошибка: 'help' не принимает аргументов.")
                return
            self.print_to_output("Доступные команды: ls, cd, help, exit")

        elif command == "ls":
            if args and any(a.startswith("-") for a in args):
                self.print_to_output("Ошибка: 'ls' не поддерживает флаги.")
                return
            self.print_to_output(f"Заглушка: 'ls' с аргументами: {args}")

        elif command == "cd":
            if len(args) > 1:
                self.print_to_output("Ошибка: 'cd' принимает максимум 1 аргумент.")
                return
            self.print_to_output(f"Заглушка: 'cd' с аргументами: {args}")

        else:
            self.print_to_output(f"Ошибка: команда '{command}' не найдена.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС — Этап 2"
    )
    parser.add_argument("--vfs-path", dest="vfs_path", type=str, default=None,
                        help="Путь к физическому расположению VFS")
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
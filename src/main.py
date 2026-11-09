import argparse
import json
import sys
import os


def load_config(config_path):
    """Загружает конфигурацию из JSON-файла."""
    if not os.path.exists(config_path):
        print(f"Ошибка: Файл конфигурации не найден: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Инструмент визуализации графа зависимостей")
    parser.add_argument("--config", dest="config_path", required=True, help="Путь к JSON-файлу конфигурации")
    args = parser.parse_args()

    config = load_config(args.config_path)

    required_keys = [
        "package_name", "repo_url", "test_mode",
        "output_file", "ascii_tree", "filter_substring"
    ]

    for key in required_keys:
        if key not in config:
            print(f"Ошибка конфигурации: отсутствует параметр '{key}'")
            sys.exit(1)

    print("--- Параметры конфигурации ---")
    print(f"Имя пакета: {config['package_name']}")
    print(f"URL репозитория: {config['repo_url']}")
    print(f"Режим тестирования: {config['test_mode']}")
    print(f"Файл изображения: {config['output_file']}")
    print(f"Вывод ASCII-дерева: {config['ascii_tree']}")
    print(f"Фильтр пакетов: {config['filter_substring']}")
    print("------------------------------")

    if config["test_mode"]:
        print(f"Внимание: Включен режим тестирования. Будет использован файл: {config['repo_url']}")
    else:
        print(f"Внимание: Режим реального репозитория. Будет использован URL: {config['repo_url']}")


if __name__ == "__main__":
    main()
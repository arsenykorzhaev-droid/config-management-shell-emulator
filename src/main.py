import argparse
import json
import sys
import os
import urllib.request
import re


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


def get_nuget_dependencies(package_name, test_mode):
    """Получает прямые зависимости пакета из NuGet."""
    if test_mode:
        # Если включен тестовый режим, возвращаем фейковые данные
        return ["Newtonsoft.Json", "Microsoft.Extensions.Logging"]

    # Реальный запрос к API NuGet
    url = f"https://api.nuget.org/v3-flatcontainer/{package_name.lower()}/index.json"

    try:
        # Получаем список версий
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            versions = data.get("versions", [])
            if not versions:
                return []

            # Берем последнюю версию
            latest_version = versions[-1]

            # Скачиваем .nuspec файл (описание пакета)
            nuspec_url = f"https://api.nuget.org/v3-flatcontainer/{package_name.lower()}/{latest_version}/{package_name.lower()}.nuspec"
            req = urllib.request.Request(nuspec_url)

            with urllib.request.urlopen(req) as res:
                nuspec_xml = res.read().decode('utf-8')

            # Ищем зависимости в XML с помощью регулярного выражения
            deps = re.findall(r'<dependency id="([^"]+)"', nuspec_xml)
            return list(set(deps))  # Убираем дубликаты
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Инструмент визуализации графа зависимостей")
    parser.add_argument("--config", dest="config_path", required=True, help="Путь к JSON-файлу конфигурации")
    args = parser.parse_args()

    config = load_config(args.config_path)

    print(f"Анализ пакета: {config['package_name']}")

    deps = get_nuget_dependencies(config['package_name'], config['test_mode'])

    print("Прямые зависимости:")
    if not deps:
        print(" (нет прямых зависимостей)")
    else:
        for dep in deps:
            print(f" - {dep}")


if __name__ == "__main__":
    main()
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
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        sys.exit(1)


def get_nuget_dependencies(package_name, test_mode):
    """Получает прямые зависимости пакета из NuGet."""
    if test_mode:
        mock_data = {
            "Newtonsoft.Json": ["System.Text.Json", "System.Runtime"],
            "System.Text.Json": ["System.Memory"],
            "System.Memory": ["System.Buffers"],
            "System.Buffers": [],
            "System.Runtime": []
        }
        return mock_data.get(package_name, [])

    base_url = "https://api.nuget.org/v3-flatcontainer"
    url = f"{base_url}/{package_name.lower()}/index.json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            versions = data.get("versions", [])
            if not versions:
                return []
            latest = versions[-1]
            nuspec_url = (
                f"{base_url}/{package_name.lower()}/{latest}/"
                f"{package_name.lower()}.nuspec"
            )
            req = urllib.request.Request(nuspec_url)
            with urllib.request.urlopen(req) as res:
                nuspec_xml = res.read().decode('utf-8')
            deps = re.findall(r'<dependency id="([^"]+)"', nuspec_xml)
            return list(set(deps))
    except Exception as e:
        return []


def build_dependency_graph(start_package, max_depth, test_mode):
    """Строит граф зависимостей с помощью BFS."""
    graph = {}
    queue = [(start_package, 0)]
    visited = set()

    while queue:
        current_pkg, depth = queue.pop(0)
        if current_pkg in visited or depth > max_depth:
            continue
        visited.add(current_pkg)
        deps = get_nuget_dependencies(current_pkg, test_mode)
        graph[current_pkg] = deps
        if depth < max_depth:
            for dep in deps:
                if dep not in visited:
                    queue.append((dep, depth + 1))
    return graph


def get_load_order(graph, node, visited=None, order=None):
    """Определяет порядок загрузки зависимостей (DFS)."""
    if visited is None:
        visited = set()
    if order is None:
        order = []

    if node in visited:
        return order
    visited.add(node)

    # Сначала обходим все зависимости
    for dep in graph.get(node, []):
        get_load_order(graph, dep, visited, order)

    # Добавляем текущий пакет в конец (после его зависимостей)
    if node not in order:
        order.append(node)
    return order


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Порядок загрузки зависимостей")
    parser.add_argument("--config", required=True, help="Путь к JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    max_depth = config.get("max_depth", 3)
    test_mode = config.get("test_mode", False)
    package = config.get("package_name", "")

    print(f"Анализ пакета: {package}")
    graph = build_dependency_graph(package, max_depth, test_mode)

    print("\nПорядок загрузки зависимостей:")
    load_order = get_load_order(graph, package)

    for i, pkg in enumerate(load_order, 1):
        print(f" {i}. {pkg}")


if __name__ == "__main__":
    main()
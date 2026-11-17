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
        print(f"Ошибка получения данных: {e}")
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


def print_ascii_tree(graph, node, prefix="", is_last=True, visited=None):
    """Выводит граф в виде текстового дерева."""
    if visited is None:
        visited = set()
    if node in visited:
        print(prefix + ("└── " if is_last else "├── ") + f"{node} (цикл)")
        return
    visited.add(node)
    print(prefix + ("└── " if is_last else "├── ") + node)
    deps = graph.get(node, [])
    for i, dep in enumerate(deps):
        is_last_dep = (i == len(deps) - 1)
        new_prefix = prefix + (" " if is_last else "│ ")
        print_ascii_tree(graph, dep, new_prefix, is_last_dep, visited.copy())


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Анализ графа зависимостей")
    parser.add_argument("--config", required=True, help="Путь к JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    max_depth = config.get("max_depth", 3)
    ascii_tree = config.get("ascii_tree", True)
    test_mode = config.get("test_mode", False)
    package = config.get("package_name", "")

    print(f"Анализ пакета: {package} (Глубина: {max_depth})")
    graph = build_dependency_graph(package, max_depth, test_mode)

    if ascii_tree:
        print("\nГраф зависимостей:")
        print_ascii_tree(graph, package)
    else:
        for pkg, deps in graph.items():
            print(f"{pkg} -> {deps}")


if __name__ == "__main__":
    main()
from __future__ import annotations

import ast
import sys
from pathlib import Path


DOMAIN_FORBIDDEN_IMPORTS = {
    "application",
    "email",
    "fastapi",
    "infrastructure",
    "pydantic",
}

APPLICATION_FORBIDDEN_IMPORTS = {
    "email",
    "fastapi",
    "infrastructure",
    "pydantic",
}


def _normalized_path(file_path: str) -> str:
    return Path(file_path).as_posix()


def _layer_for_file(file_path: str) -> str | None:
    normalized_path = _normalized_path(file_path)

    if normalized_path.startswith("src/domain/"):
        return "domain"

    if normalized_path.startswith("src/application/"):
        return "application"

    return None


def _forbidden_imports_for_layer(layer: str) -> set[str]:
    if layer == "domain":
        return DOMAIN_FORBIDDEN_IMPORTS

    if layer == "application":
        return APPLICATION_FORBIDDEN_IMPORTS

    return set()


def _import_target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]

    if isinstance(node, ast.ImportFrom) and node.module is not None:
        return [node.module]

    return []


def _violations_for_file(file_path: str) -> list[str]:
    layer = _layer_for_file(file_path)
    if layer is None:
        return []

    source_path = Path(file_path)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=file_path)
    forbidden_imports = _forbidden_imports_for_layer(layer)
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        for import_name in _import_target_names(node):
            top_level_name = import_name.split(".", 1)[0]
            if top_level_name in forbidden_imports:
                violations.append(
                    f"{file_path}:{node.lineno} imports '{import_name}' inside {layer}, which breaks the expected architecture boundary.",
                )

    return violations


def main() -> int:
    file_paths = [file_path for file_path in sys.argv[1:] if Path(file_path).is_file()]
    violations: list[str] = []

    for file_path in file_paths:
        violations.extend(_violations_for_file(file_path))

    if not violations:
        return 0

    print("Architecture boundary check failed:")
    for violation in violations:
        print(f"- {violation}")

    print("Allowed direction remains: Domain <- Application <- Infrastructure / Entrypoints.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Simple tree generator for project structure.
Usage: python generate_tree.py <directory> [max_depth]
"""
import os
import sys


def generate_tree(directory, prefix="", max_depth=None, current_depth=0):
    """Generate a tree structure of a directory."""
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return

    # Filter out common unneeded files
    ignore_patterns = [
        "__pycache__",
        ".pyc",
        ".pytest_cache",
        ".git",
        "node_modules",
        ".venv",
        "venv",
        ".egg-info",
    ]

    entries = [
        e for e in entries if not any(pattern in e for pattern in ignore_patterns)
    ]

    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1

        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{entry}")

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            generate_tree(
                path,
                prefix + extension,
                max_depth,
                current_depth + 1,
            )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_tree.py <directory> [max_depth]")
        sys.exit(1)

    target_dir = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a directory")
        sys.exit(1)

    print(target_dir)
    generate_tree(target_dir, max_depth=max_depth)

#!/usr/bin/env python3
"""
Small script that can parse TOML files without any dependencies
"""
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Optional
from typing import Union

if sys.version_info >= (3, 11):
    # use the standard library module
    from tomllib import load

else:
    from tomli import load


def parse_args():
    """
    Main module
    """
    parser = ArgumentParser(
        description=(
            "Parse a pyproject.toml file and output dependencies "
            "in requirements.txt format"
        ),
    )
    parser.add_argument(
        "file",
        help="the path to the pyproject.toml file",
    )
    parser.add_argument(
        "--runtime",
        "-r",
        action="store_false",
        help="do not show runtime dependencies",
    )
    parser.add_argument(
        "--build",
        "-b",
        action="store_false",
        help="do not show build dependencies",
    )
    parser.add_argument(
        "--type",
        "-t",
        help=(
            "the type of optional dependency to show "
            "(default: show packages from all optional dependency types)"
        ),
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="list all of the optional dependency types. "
        "Note that this overrides all other options",
    )
    return parser.parse_args()


def parse_file(file: Union[str, Path], /) -> dict:
    """
    Parse the ``pyproject.toml`` file
    """

    if not Path(file).exists():
        raise FileNotFoundError(f"File {file} not found")
    with open(file, "rb") as f:
        content = load(f)

    return content


def parse_array_specifier(
    data: dict,
    specifier: str,
    *,
    strict: bool = False,
) -> list[str]:
    """
    Parse a given specifier and return the contents
    """
    keys = specifier.split(".")
    # copy of the data
    result = {**data}
    for index, key in enumerate(keys):
        if key not in result:
            if strict:
                raise KeyError(
                    f"The specifier {key} at position {index} (0-indexed) of '{specifier}' is invalid"
                )
            result = result.get(key, {})
        else:
            result = result[key]

    return list(result)


def main():
    args = parse_args()

    content = parse_file(args.file)

    deps = {
        "build-system": [],
        "dependencies": [],
        "optional-dependencies": defaultdict(list),
    }

    if args.list:
        for key in parse_array_specifier(content, "project.optional-dependencies"):
            print(key)
        return

    if args.build:
        for package in parse_array_specifier(content, "build-system.requires"):
            deps["build-system"].append(package)

    if args.runtime:
        for package in parse_array_specifier(content, "project.dependencies"):
            deps["dependencies"].append(package)

    if args.type:
        for package in parse_array_specifier(
            content, f"project.optional-dependencies.{args.type}"
        ):
            deps["optional-dependencies"][args.type].append(package)
    else:
        opt_dep_types = parse_array_specifier(content, "project.optional-dependencies")
        for opt_dep in opt_dep_types:
            for package in parse_array_specifier(
                content, f"project.optional-dependencies.{opt_dep}"
            ):
                deps["optional-dependencies"][opt_dep].append(package)

    if deps["build-system"]:
        print("# build time dependencies")
        for package in deps["build-system"]:
            print(package)

    if deps["dependencies"]:
        print("# run time dependencies")
        for package in deps["dependencies"]:
            print(package)

    if deps["optional-dependencies"]:
        for dep in deps["optional-dependencies"]:
            print(f"# optional dependencies for {dep}")
            for package in deps["optional-dependencies"][dep]:
                print(package)


if __name__ == "__main__":
    main()

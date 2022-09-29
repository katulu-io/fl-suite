import inspect
import itertools
import os
import re
import textwrap
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from tempfile import mkdtemp
from typing import Callable, List, Optional


@dataclass(init=False)
class Context:
    """Defines a all files associated with container context"""

    base_dir: Path
    file_paths: List[Path]
    entrypoint: List[str]

    def __init__(self, base_dir: Path, entrypoint: List[str]):
        self.base_dir = base_dir
        self.file_paths = []
        for subdir, _, files in os.walk(base_dir):
            for file in files:
                self.file_paths.append(Path(os.path.join(subdir, file)))
        self.entrypoint = entrypoint


def context_from_func(
    file_path: str = "main.py",
    base_image: str = "python:3.10",
    packages: Optional[List[str]] = None,
) -> Callable[[Callable[[], None]], Callable[[], Context]]:
    """Decorator for a Federated Learning client implementation."""
    if packages is None:
        packages = []

    def _wrapped(func: Callable[[], None]) -> Callable[[], Context]:
        func_code = textwrap.dedent(inspect.getsource(func))

        func_code_lines = func_code.split("\n")

        # Removing possible decorators (can be multiline) until the function
        # definition is found
        func_code_lines = list(
            itertools.dropwhile(lambda x: not x.startswith("def"), func_code_lines)
        )

        func_code = textwrap.dedent("\n".join(func_code_lines[1:]))

        @wraps(func)
        def _inner() -> Context:
            base_dir = Path(mkdtemp())
            entrypoint_dirname_str, entrypoint_basename_str = os.path.split(base_dir / file_path)
            entrypoint_dirname = Path(entrypoint_dirname_str)
            entrypoint_dirname.mkdir(parents=True, exist_ok=True)

            with open(entrypoint_dirname / entrypoint_basename_str, "w", encoding="utf-8") as main:
                main.write(func_code)

            return context_from_python_files(
                src_dir=str(base_dir),
                entrypoint=["python3", file_path],
                base_image=base_image,
                python_packages=packages,
            )

        return _inner

    return _wrapped


# pylint: disable-next=too-many-arguments
def context_from_python_files(
    src_dir: str,
    entrypoint: Optional[List[str]] = None,
    base_image: str = "python:3.10",
    python_packages: Optional[List[str]] = None,
) -> Context:
    """Prepares docker context based on a directory and uploads it to minio (bucket_name)"""
    if entrypoint is None:
        entrypoint = ["python3", "main.py"]

    if python_packages is None:
        python_packages = []

    top_level = os.listdir(src_dir)
    requirements_txt_exists = "requirements.txt" in top_level

    _create_dockerfile(src_dir, entrypoint, base_image, requirements_txt_exists, python_packages)

    context = Context(Path(src_dir), entrypoint=entrypoint)

    return context


def _create_dockerfile(
    src_dir: str,
    entrypoint: List[str],
    base_image: str,
    exists_requirements_txt: bool,
    python_packages: List[str],
):
    install_dependencies_instruction = ""
    if exists_requirements_txt:
        install_dependencies_instruction = (
            "RUN python -m pip install --no-cache-dir -r /app/requirements.txt"
        )
    elif len(python_packages) > 0:
        install_dependencies_instruction = (
            f"RUN python -m pip install --no-cache-dir {' '.join(python_packages)}"
        )

    entrypoint_str = ", ".join(f'"{e}"' for e in entrypoint)
    dockerfile_content = f"""FROM {base_image}
COPY . /app/
{install_dependencies_instruction}
WORKDIR /app
ENTRYPOINT [ {entrypoint_str} ]
"""
    with open(Path(src_dir) / "Dockerfile", "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)


def context_from_dockerfile(src_dir: str):
    """Expects Dockerfile to exist in src_dir and uploads it to minio (bucket_name)"""
    dockerfile = Path(src_dir) / "Dockerfile"
    if not dockerfile.exists():
        raise MissingDockerfile(f'"Dockerfile" not found in: {dockerfile}')

    entrypoint_match = re.search(r"ENTRYPOINT \[?(.*?)\]?\n", dockerfile.read_text())
    if not entrypoint_match:
        raise MissingEntrypoint(f'Missing required ENTRYPOINT in "Dockerfile" in: {dockerfile}')

    entrypoint_line = entrypoint_match.group(1)
    entrypoint_line = re.sub(r'[",]', "", entrypoint_line).strip()
    entrypoint = entrypoint_line.split(" ")

    context = Context(Path(src_dir), entrypoint=entrypoint)

    return context


class MissingDockerfile(Exception):
    """Custom exception to represent a missing dockerfile"""


class MissingEntrypoint(Exception):
    """Custom exception to represent a missing entrypoint in the dockerfile"""

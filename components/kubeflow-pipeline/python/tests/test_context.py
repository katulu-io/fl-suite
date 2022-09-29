from pathlib import Path
from typing import Dict, List

import pytest

from fl_suite.context import (
    Context,
    MissingDockerfile,
    MissingEntrypoint,
    context_from_func,
    context_from_dockerfile,
    context_from_python_files,
)


def test_context_from_func() -> None:
    """Test context_from_dir_with_requirements with a requirements.txt file and mocked resources"""

    @context_from_func(packages=["tensorflow", "flwr==1.0.0"])
    def hello_world():
        print("hola mundo")

    context = hello_world()

    assert_context(
        context,
        {
            context.base_dir
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir tensorflow flwr==1.0.0
WORKDIR /app
ENTRYPOINT [ "python3", "main.py" ]
""",
            context.base_dir / "main.py": 'print("hola mundo")\n',
        },
        ["python3", "main.py"],
    )


def test_context_from_func_with_custom_entrypoint() -> None:
    """Test context_from_dir_with_requirements with a requirements.txt file and mocked resources"""

    @context_from_func(file_path="flwr_server/__main__.py", packages=["tensorflow", "flwr==1.0.0"])
    def hello_world():
        print("hola mundo")

    context = hello_world()

    assert_context(
        context,
        {
            context.base_dir
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir tensorflow flwr==1.0.0
WORKDIR /app
ENTRYPOINT [ "python3", "flwr_server/__main__.py" ]
""",
            context.base_dir / "flwr_server/__main__.py": 'print("hola mundo")\n',
        },
        ["python3", "flwr_server/__main__.py"],
    )


def test_context_from_python_files_with_requirements(dir_with_requirements: Path) -> None:
    """Test context_from_dir_with_requirements with a requirements.txt file and mocked resources"""

    context = context_from_python_files(
        src_dir=str(dir_with_requirements),
        entrypoint=["python3", "main.py"],
    )

    assert_context(
        context,
        {
            dir_with_requirements
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT [ "python3", "main.py" ]
""",
            dir_with_requirements / "requirements.txt": "flwr",
            dir_with_requirements / "main.py": 'print("hello")',
            dir_with_requirements / "lib" / "test.py": 'print("another function")',
        },
        ["python3", "main.py"],
    )


def test_context_from_python_files_without_requirements(dir_without_requirements: Path) -> None:
    """Test context_from_dir without a requirements.txt file and mocked resources"""

    context = context_from_python_files(
        src_dir=str(dir_without_requirements),
        entrypoint=["python3", "main.py"],
        python_packages=["torch", "flwr"],
    )

    assert_context(
        context,
        {
            dir_without_requirements
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch flwr
WORKDIR /app
ENTRYPOINT [ "python3", "main.py" ]
""",
            dir_without_requirements / "main.py": 'print("hello")',
            dir_without_requirements / "lib" / "test.py": 'print("another function")',
        },
        ["python3", "main.py"],
    )


def test_context_from_dockerfile_with_exec_form_entrypoint(
    dir_with_dockerfile_with_exec_form_entrypoint: Path,
) -> None:
    """Test context_from_dockerfile with dockerfile and an entrypoint with exec form"""
    context = context_from_dockerfile(str(dir_with_dockerfile_with_exec_form_entrypoint))

    assert_context(
        context,
        {
            dir_with_dockerfile_with_exec_form_entrypoint
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT [ "python", "/app/main.py" ]
""",
            dir_with_dockerfile_with_exec_form_entrypoint / "main.py": 'print("hello")',
        },
        ["python", "/app/main.py"],
    )


def test_context_from_dockerfile_with_shell_form_entrypoint(
    dir_with_dockerfile_with_shell_form_entrypoint: Path,
) -> None:
    """Test context_from_dockerfile with dockerfile and an entrypoint with shell form"""
    context = context_from_dockerfile(str(dir_with_dockerfile_with_shell_form_entrypoint))

    assert_context(
        context,
        {
            dir_with_dockerfile_with_shell_form_entrypoint
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT python /app/main.py
""",
            dir_with_dockerfile_with_shell_form_entrypoint / "main.py": 'print("hello")',
        },
        ["python", "/app/main.py"],
    )


def test_context_from_dockerfile_without_dockerfile(dir_with_requirements: Path) -> None:
    """Test context_from_dockerfile without dockerfile"""

    with pytest.raises(MissingDockerfile) as _:
        context_from_dockerfile(str(dir_with_requirements))


def test_context_from_dockerfile_without_entrypoint(
    dir_with_dockerfile_without_entrypoint: Path,
) -> None:
    """Test context_from_dockerfile without entrypoint"""

    with pytest.raises(MissingEntrypoint) as _:
        context_from_dockerfile(str(dir_with_dockerfile_without_entrypoint))


def assert_context(
    context: Context, expected_path_content_mapping: Dict[Path, str], expected_entrypoint: List[str]
):
    """Asserts the content of a path has the expected content"""

    assert sorted(list(expected_path_content_mapping.keys())) == sorted(
        context.file_paths
    ), "Missing expected file"
    for path in context.file_paths:
        expected_content = expected_path_content_mapping[path]
        assert expected_content == path.read_text()

    assert context.entrypoint == expected_entrypoint

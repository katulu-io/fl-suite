from pathlib import Path
import pytest


@pytest.fixture(name="dir_with_requirements")
def fixture_dir_with_requirements(tmp_path: Path):
    """Creates a temporary directory (context) with a requirements.txt file"""

    src_dir = tmp_path / "client"
    src_dir.mkdir()

    main_file = src_dir / "main.py"
    main_file.write_text('print("hello")')

    lib_dir = src_dir / "lib"
    lib_dir.mkdir()
    py_file = lib_dir / "test.py"
    py_file.write_text('print("another function")')

    requirements_txt = src_dir / "requirements.txt"
    requirements_txt.write_text("flwr")

    return src_dir


@pytest.fixture(name="flwr_server_context")
def fixture_flwr_server_context(tmp_path: Path):
    """Creates a temporary directory (context) with a requirements.txt file"""

    src_dir = tmp_path / "mnist"
    src_dir.mkdir()

    requirements_txt = src_dir / "requirements.txt"
    requirements_txt.write_text("flwr")

    lib_dir = src_dir / "flwr_server"
    lib_dir.mkdir()

    main_file = lib_dir / "__main__.py"
    main_file.write_text('print("hello")')

    py_file = lib_dir / "strategy.py"
    py_file.write_text('print("another function")')

    return src_dir


@pytest.fixture(name="dir_without_requirements")
def fixture_dir_without_requirements(tmp_path: Path):
    """Creates a temporary directory (context) without a requirements.txt file"""

    src_dir = tmp_path / "client"
    src_dir.mkdir()

    main_file = src_dir / "main.py"
    main_file.write_text('print("hello")')

    lib_dir = src_dir / "lib"
    lib_dir.mkdir()
    py_file = lib_dir / "test.py"
    py_file.write_text('print("another function")')

    return src_dir


@pytest.fixture(name="dir_with_dockerfile_with_exec_form_entrypoint")
def fixture_dir_with_dockerfile_with_exec_form_entrypoint(tmp_path: Path):
    """Creates a temporary directory (context) with a predefined Dockerfile"""

    src_dir = tmp_path / "client-with-dockerfile"
    src_dir.mkdir()

    main_file = src_dir / "main.py"
    main_file.write_text('print("hello")')

    dockerfile = src_dir / "Dockerfile"
    dockerfile.write_text(
        """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT [ "python", "/app/main.py" ]
"""
    )

    return src_dir


@pytest.fixture(name="dir_with_dockerfile_with_shell_form_entrypoint")
def fixture_dir_with_dockerfile_with_shell_form_entrypoint(tmp_path: Path):
    """Creates a temporary directory (context) with a predefined Dockerfile"""

    src_dir = tmp_path / "client-with-dockerfile"
    src_dir.mkdir()

    main_file = src_dir / "main.py"
    main_file.write_text('print("hello")')

    dockerfile = src_dir / "Dockerfile"
    dockerfile.write_text(
        """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT python /app/main.py
"""
    )

    return src_dir


@pytest.fixture(name="dir_with_dockerfile_without_entrypoint")
def fixture_dir_with_dockerfile_without_entrypoint(tmp_path: Path):
    """Creates a temporary directory (context) with a Dockerfile without entrypoint"""

    src_dir = tmp_path / "client-with-dockerfile"
    src_dir.mkdir()

    main_file = src_dir / "main.py"
    main_file.write_text('print("hello")')

    dockerfile = src_dir / "Dockerfile"
    dockerfile.write_text(
        """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
"""
    )

    return src_dir

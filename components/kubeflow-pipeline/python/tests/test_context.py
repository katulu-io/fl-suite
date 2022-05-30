from pathlib import Path
from typing import Any, Dict, List, Union
from unittest.mock import MagicMock, call

import pytest

from fl_suite.context import (
    Context,
    MissingDockerfile,
    context_from_dockerfile,
    context_from_python_files,
    upload_context_to_minio,
)


def test_context_from_python_files_with_requirements(dir_with_requirements: Path) -> None:
    """Test context_from_dir_with_requirements with a requirements.txt file and mocked resources"""

    context = context_from_python_files(
        src_dir=str(dir_with_requirements),
        entrypoint="main.py",
    )

    assert_context(
        context,
        {
            dir_with_requirements
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir -r /app/requirements.txt
ENTRYPOINT [ "python", "/app/main.py" ]
""",
            dir_with_requirements / "requirements.txt": "flwr",
            dir_with_requirements / "main.py": 'print("hello")',
            dir_with_requirements / "lib" / "test.py": 'print("another function")',
        },
    )


def test_context_from_python_files_without_requirements(dir_without_requirements: Path) -> None:
    """Test context_from_dir without a requirements.txt file and mocked resources"""

    context = context_from_python_files(
        src_dir=str(dir_without_requirements),
        entrypoint="main.py",
        python_packages=["torch", "flwr"],
    )

    assert_context(
        context,
        {
            dir_without_requirements
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT [ "python", "/app/main.py" ]
""",
            dir_without_requirements / "main.py": 'print("hello")',
            dir_without_requirements / "lib" / "test.py": 'print("another function")',
        },
    )


def test_context_from_dockerfile(dir_with_dockerfile: Path) -> None:
    """Test context_from_dockerfile with mocked resources"""
    context = context_from_dockerfile(str(dir_with_dockerfile))

    assert_context(
        context,
        {
            dir_with_dockerfile
            / "Dockerfile": """FROM python:3.10
COPY . /app/
RUN python -m pip install --no-cache-dir torch, flwr
ENTRYPOINT [ "python", "/app/main.py" ]
""",
            dir_with_dockerfile / "main.py": 'print("hello")',
        },
    )


def test_context_from_dockerfile_without_dockerfile(dir_with_requirements: Path) -> None:
    """Test context_from_dockerfile with mocked resources"""
    with pytest.raises(MissingDockerfile) as _:
        context_from_dockerfile(str(dir_with_requirements))


def test_upload_context_to_minio(dir_with_dockerfile: Path, minio_client_mock: MagicMock):
    """Test upload_context_to_minio with mocked resources"""

    context = Context(dir_with_dockerfile)

    upload_context_to_minio(
        context=context,
        dest_path="test/client",
        minio_client=minio_client_mock,
    )

    assert_minio_upload(
        minio_client_mock,
        "fl-suite-build-context",
        [
            ["test/client/Dockerfile", dir_with_dockerfile / "Dockerfile"],
            ["test/client/main.py", dir_with_dockerfile / "main.py"],
        ],
    )


@pytest.fixture(name="minio_client_mock")
def fixture_minio_client_mock() -> MagicMock:
    """Creates a mocked minio client"""
    mock = MagicMock()
    mock.bucket_exists.return_value = True

    return mock


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


@pytest.fixture(name="dir_with_dockerfile")
def fixture_dir_with_dockerfile(tmp_path: Path):
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


def assert_context(context: Context, expected_path_content_mapping: Dict[Path, str]):
    """Asserts the content of a path has the expected content"""

    assert sorted(list(expected_path_content_mapping.keys())) == sorted(context.file_paths)
    for path in context.file_paths:
        expected_content = expected_path_content_mapping[path]
        assert expected_content == path.read_text()


def assert_minio_upload(
    minio_client_mock: MagicMock, bucket_name: str, path_tuple_list: List[List[Union[str, Path]]]
):
    """Asserts that the minio client uploaded the specified files"""

    call_list: List[Any] = []
    for remote_dest, local_path in path_tuple_list:
        call_list.append(call(bucket_name, remote_dest, local_path))

    minio_client_mock.fput_object.assert_has_calls(call_list, any_order=True)

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from minio import Minio


@dataclass(init=False)
class Context:
    """Defines a all files associated with container context"""

    base_dir: Path
    file_paths: List[Path]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.file_paths = []
        for subdir, _, files in os.walk(base_dir):
            for file in files:
                self.file_paths.append(Path(os.path.join(subdir, file)))


# pylint: disable-next=too-many-arguments
def context_from_python_files(
    src_dir: str,
    entrypoint: str = "",
    base_image: str = "python:3.10",
    python_packages: Optional[List[str]] = None,
) -> Context:
    """Prepares docker context based on a directory and uploads it to minio (bucket_name)"""
    if python_packages is None:
        python_packages = []

    top_level = os.listdir(src_dir)
    requirements_txt_exists = "requirements.txt" in top_level

    _create_dockerfile(src_dir, entrypoint, base_image, requirements_txt_exists, python_packages)

    context = Context(Path(src_dir))

    return context


def _create_dockerfile(
    src_dir: str,
    entrypoint: str,
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
            f"RUN python -m pip install --no-cache-dir {', '.join(python_packages)}"
        )

    dockerfile_content = f"""FROM {base_image}
COPY . /app/
{install_dependencies_instruction}
ENTRYPOINT [ "python", "/app/{entrypoint}" ]
"""
    with open(Path(src_dir) / "Dockerfile", "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)


def context_from_dockerfile(src_dir: str):
    """Expects Dockerfile to exist in src_dir and uploads it to minio (bucket_name)"""
    top_level = os.listdir(src_dir)
    if "Dockerfile" not in top_level:
        raise MissingDockerfile(f'Missing required "Dockerfile" in {top_level}')

    context = Context(Path(src_dir))

    return context


def _read_secret_file(filepath: str) -> str:
    with open(filepath, encoding="utf-8") as secret_file:
        content = secret_file.read()

    return content.splitlines()[0]


def upload_context_to_minio(
    context: Context,
    dest_path: str,
    minio_client: Optional[Minio] = None,
    bucket_name: str = "fl-suite-build-context",
) -> str:
    """Uploads a context minio"""

    if minio_client is None:
        minio_client = Minio(
            "minio-service.kubeflow:9000",
            access_key=_read_secret_file("/minio/accesskey"),
            secret_key=_read_secret_file("/minio/secretkey"),
            secure=False,
        )

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    for path in context.file_paths:
        remote_path = os.path.relpath(path, context.base_dir)
        minio_client.fput_object(
            bucket_name,
            f"{dest_path}/{remote_path}",
            path,
        )

    return f"{bucket_name}/{dest_path}"


class MissingDockerfile(Exception):
    """Custom exception to represent a missing dockerfile"""

import inspect
import itertools
import textwrap
from functools import wraps
from typing import Callable, List, Optional

from kfp.v2.dsl import ContainerOp

from ._prepare_context import prepare_context


def fl_client(
    base_image: str = "python:3.10",
    packages: Optional[List[str]] = None,
) -> Callable[[Callable[[], None]], ContainerOp]:
    """Decorator for a Federated Learning client implementation."""
    if packages is None:
        packages = []

    def _wrapped(func: Callable[[], None]) -> Callable[[], ContainerOp]:
        func_code = textwrap.dedent(inspect.getsource(func))

        func_code_lines = func_code.split("\n")

        # Removing possible decorators (can be multiline) until the function
        # definition is found
        func_code_lines = list(
            itertools.dropwhile(lambda x: not x.startswith("def"), func_code_lines)
        )

        func_code = textwrap.dedent("\n".join(func_code_lines[1:]))

        @wraps(func)
        def _inner() -> ContainerOp:
            return prepare_context(func_code, base_image, packages)

        return _inner

    return _wrapped

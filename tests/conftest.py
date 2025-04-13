import os
import pytest


@pytest.fixture
def name_file():
    full_name: str = os.path.abspath(__name__)
    name_dir: str = os.path.dirname(full_name)
    if "tests" in name_dir:
        name_file: str = os.path.join(name_dir, "app.log")
    else:
        name_file: str = os.path.join(name_dir, "tests", "app.log")
    return name_file

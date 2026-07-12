import os
import pytest
from config import REPO_ROOT

def test_repo_root_is_absolute():
    assert os.path.isabs(REPO_ROOT)
    assert os.path.basename(REPO_ROOT) == "aisci"


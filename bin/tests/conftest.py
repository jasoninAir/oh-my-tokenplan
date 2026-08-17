"""pytest fixtures for bin/agents tests."""
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """复制 fixtures/sample_project 到临时目录，返回路径。"""
    src = FIXTURES / "sample_project"
    dst = tmp_path / "sample_project"
    shutil.copytree(src, dst)
    return dst


@pytest.fixture
def run_agents():
    """返回在指定项目目录运行 bin/agents 的辅助函数。"""
    import subprocess

    BIN = Path(__file__).parent.parent / "agents"

    def _run(project: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(BIN), *args],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )

    return _run
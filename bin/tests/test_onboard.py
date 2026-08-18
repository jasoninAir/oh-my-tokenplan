"""测试 bin/agentrace onboard。"""
import subprocess
from pathlib import Path


def test_onboard_creates_agents_md_and_plan(tmp_path, run_agents):
    """onboard 应创建 AGENTS.md 和 .agents/onboarding-plan.yaml。"""
    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    assert (tmp_path / "AGENTS.md").exists()
    plan = tmp_path / ".agents/onboarding-plan.yaml"
    assert plan.exists()
    content = plan.read_text()
    assert "project_type" in content
    assert "modules" in content


def test_onboard_detects_python_project(tmp_path, run_agents):
    """onboard 在 Python 项目（pyproject.toml）应识别 project_type=python。"""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\ndependencies=['fastapi']\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/auth").mkdir()
    (tmp_path / "src/auth/__init__.py").write_text("# auth module")
    (tmp_path / "src/auth/login.py").write_text("def login(): pass\n")
    (tmp_path / "src/auth/test_login.py").write_text("# tests")

    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    import yaml
    plan = yaml.safe_load((tmp_path / ".agents/onboarding-plan.yaml").read_text())
    assert plan["project_type"] == "python"
    assert "fastapi" in plan["frameworks"]
    paths = [m["path"] for m in plan["modules"]]
    assert "src/auth" in paths


def test_onboard_detects_node_project(tmp_path, run_agents):
    """onboard 在 Node 项目应识别 project_type=nodejs。"""
    import json
    pkg = {
        "name": "blog",
        "dependencies": {"react": "^18", "next": "^14"},
        "devDependencies": {},
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    (tmp_path / "src").mkdir()
    (tmp_path / "src/articles").mkdir()
    (tmp_path / "src/articles/index.ts").write_text("export const Articles = 1;\n" * 3)

    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    import yaml
    plan = yaml.safe_load((tmp_path / ".agents/onboarding-plan.yaml").read_text())
    assert plan["project_type"] == "nodejs"
    assert any(fw in plan["frameworks"] for fw in ("react", "next"))


def test_onboard_skips_test_and_node_modules_dirs(tmp_path, run_agents):
    """onboard 应跳过 tests / node_modules / __pycache__ 等。"""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/auth").mkdir()
    (tmp_path / "src/auth/core.py").write_text("x = 1\n")
    # 这些目录应该被排除
    for skip in ("tests", "node_modules", "__pycache__", "docs", "scripts"):
        d = tmp_path / "src" / skip
        d.mkdir()
        (d / "stuff.py").write_text("y = 1\n")

    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    import yaml
    plan = yaml.safe_load((tmp_path / ".agents/onboarding-plan.yaml").read_text())
    paths = [m["path"] for m in plan["modules"]]
    assert "src/auth" in paths
    # 跳过的目录不应出现
    for skip in ("tests", "node_modules", "__pycache__", "docs", "scripts"):
        assert not any(skip in p for p in paths), f"should skip {skip}, got {paths}"


def test_onboard_skips_init_when_agents_md_exists(tmp_path, run_agents):
    """onboard 在 AGENTS.md 已存在时跳过 init。"""
    (tmp_path / "AGENTS.md").write_text("# existing\n")
    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "AGENTS.md").read_text() == "# existing\n"  # 不覆盖


def test_onboard_counts_commits_per_module(tmp_path, run_agents):
    """onboard 应统计每个模块的 commit 数量。"""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/auth").mkdir()
    (tmp_path / "src/auth/__init__.py").write_text("x = 1\n")
    (tmp_path / "src/posts").mkdir()
    (tmp_path / "src/posts/__init__.py").write_text("y = 1\n")

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "auth scaffold"],
        cwd=tmp_path, capture_output=True,
    )
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-m", "tweak auth"],
        cwd=tmp_path, capture_output=True,
    )
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-m", "posts start"],
        cwd=tmp_path, capture_output=True,
    )

    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    import yaml
    plan = yaml.safe_load((tmp_path / ".agents/onboarding-plan.yaml").read_text())
    by_path = {m["path"]: m for m in plan["modules"]}
    # 初始 commit 把所有文件 add 进 src/auth 和 src/posts
    # 之后两个 --allow-empty commit 不产生 name-only 输出
    assert by_path["src/auth"]["commit_count"] >= 1
    assert by_path["src/posts"]["commit_count"] >= 1
    # confidence 应都 > 0（因为有 file_count + commit_count）
    assert by_path["src/auth"]["confidence"] > 0
    assert by_path["src/posts"]["confidence"] > 0


def test_onboard_empty_project_does_not_crash(tmp_path, run_agents):
    """onboard 在空项目应仍跑通（plan 里 modules 为空）。"""
    result = run_agents(tmp_path, "onboard")
    assert result.returncode == 0, result.stderr

    import yaml
    plan = yaml.safe_load((tmp_path / ".agents/onboarding-plan.yaml").read_text())
    assert plan["modules"] == []
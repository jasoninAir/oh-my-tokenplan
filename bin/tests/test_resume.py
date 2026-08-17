"""测试 bin/agentrace resume / triage。"""
import subprocess


def test_resume_clean_workspace(tmp_path, run_agents):
    """干净工作区下 resume 应输出简报标题。"""
    run_agents(tmp_path, "init")
    result = run_agents(tmp_path, "resume")
    assert result.returncode == 0, result.stderr
    assert "现场接力简报" in result.stdout


def test_resume_dirty_workspace(tmp_path, run_agents):
    """有未提交改动时 resume 应提取修改文件与符号提示。"""
    run_agents(tmp_path, "init")
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

    test_file = tmp_path / "foo.py"
    test_file.write_text("def calculate_tax(amount):\n    return amount * 0.1\n")

    result = run_agents(tmp_path, "resume")
    assert result.returncode == 0, result.stderr
    assert "foo.py" in result.stdout
    assert "calculate_tax" in result.stdout


def test_triage_is_resume_alias(tmp_path, run_agents):
    """triage 是 resume 的别名。"""
    run_agents(tmp_path, "init")
    r1 = run_agents(tmp_path, "resume")
    r2 = run_agents(tmp_path, "triage")
    assert r1.returncode == 0 and r2.returncode == 0
    assert "现场接力简报" in r1.stdout
    assert "现场接力简报" in r2.stdout
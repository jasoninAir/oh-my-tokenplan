"""测试 bin/agents impact。"""


def test_impact_finds_symbol_callers(tmp_path, run_agents):
    """impact 命令应找到目标符号所在的文件。"""
    (tmp_path / "core.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "use.py").write_text("from core import add\nx = add(1, 2)\n")

    result = run_agents(tmp_path, "impact", "add")
    assert result.returncode == 0, result.stderr
    assert "core.py" in result.stdout
    assert "use.py" in result.stdout


def test_impact_missing_target_fails(tmp_path, run_agents):
    """impact 不带 target 应失败。"""
    result = run_agents(tmp_path, "impact")
    assert result.returncode != 0
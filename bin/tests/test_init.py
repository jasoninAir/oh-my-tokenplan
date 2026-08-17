"""测试 bin/agents init。"""


def test_init_creates_structure(tmp_path, run_agents):
    """init 应创建 docs/agents/stories 等目录。"""
    result = run_agents(tmp_path, "init")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "docs/agents/stories").exists()
    assert (tmp_path / "docs/agents/reviews").exists()
    assert (tmp_path / "AGENTS.md").exists()


def test_init_refuses_existing(tmp_path, run_agents):
    """init 应在已存在 AGENTS.md 的目录拒绝。"""
    (tmp_path / "AGENTS.md").write_text("# existing\n")
    result = run_agents(tmp_path, "init")
    assert result.returncode != 0
    assert "exists" in result.stderr.lower() or "已存在" in result.stderr
"""测试 bin/agentrace render。"""


def test_render_creates_overview(sample_project, run_agents):
    """render 应生成 docs/agentrace/OVERVIEW.md。"""
    result = run_agents(sample_project, "render")
    assert result.returncode == 0, result.stderr
    overview = sample_project / "docs/agentrace/OVERVIEW.md"
    assert overview.exists()
    content = overview.read_text()
    assert "S-001" in content
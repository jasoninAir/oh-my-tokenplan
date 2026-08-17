"""测试 bin/agentrace sync。"""


def test_sync_updates_agents_md_table(sample_project, run_agents):
    """sync 应在 AGENTS.md 的"当前激活 Story"表中反映所有 Story。"""
    agents_md = sample_project / "AGENTS.md"
    agents_md.write_text("# AGENTS\n\n## 当前激活 Story\n\n<!-- bin/agentrace sync -->\n\n## 路线图\n")

    run_agents(sample_project, "sync")
    content = agents_md.read_text()
    assert "S-001" in content
    assert "Test story" in content or "test" in content.lower()
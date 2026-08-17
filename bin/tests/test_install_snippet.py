"""测试 bin/agentrace install-snippet。"""
from pathlib import Path


def test_install_snippet_creates_marker(tmp_path, monkeypatch, run_agents):
    """install-snippet 应在 ~/.claude/CLAUDE.md 加 BEGIN/END 标记。"""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()
    (fake_claude / "CLAUDE.md").write_text("# existing\n")

    monkeypatch.setenv("HOME", str(fake_home))
    # 在 tmp_path 下放 snippet 文件（cmd_install_snippet 找 cwd/adapters/snippets/）
    snippet_dir = tmp_path / "adapters/snippets"
    snippet_dir.mkdir(parents=True)
    (snippet_dir / "claude.md").write_text(
        "<!-- BEGIN agentrace-protocol v0.1 -->\nclaude snippet content\n<!-- END agentrace-protocol v0.1 -->\n"
    )
    result = run_agents(tmp_path, "install-snippet", "--agent", "claude")
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"

    installed = (fake_claude / "CLAUDE.md").read_text()
    assert "BEGIN agentrace-protocol" in installed
    assert "END agentrace-protocol" in installed


def test_install_snippet_idempotent(tmp_path, monkeypatch, run_agents):
    """第二次运行 install-snippet 不应重复追加。"""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()
    (fake_claude / "CLAUDE.md").write_text("# existing\n")

    monkeypatch.setenv("HOME", str(fake_home))
    snippet_dir = tmp_path / "adapters/snippets"
    snippet_dir.mkdir(parents=True)
    (snippet_dir / "claude.md").write_text(
        "<!-- BEGIN agentrace-protocol v0.1 -->\nclaude snippet content\n<!-- END agentrace-protocol v0.1 -->\n"
    )
    run_agents(tmp_path, "install-snippet", "--agent", "claude")
    first_content = (fake_claude / "CLAUDE.md").read_text()
    run_agents(tmp_path, "install-snippet", "--agent", "claude")
    second_content = (fake_claude / "CLAUDE.md").read_text()
    assert first_content == second_content
"""测试 bin/agents new-story。"""
from pathlib import Path


def test_new_story_creates_file(sample_project, run_agents):
    result = run_agents(sample_project, "new-story", "--title", "new feature")
    assert result.returncode == 0, result.stderr
    created = sample_project / "docs/agents/stories/S-002-new-feature.md"
    assert created.exists()


def test_new_story_assigns_next_id(sample_project, run_agents):
    result = run_agents(sample_project, "new-story", "--title", "another")
    assert result.returncode == 0
    files = list((sample_project / "docs/agents/stories").glob("S-*.md"))
    assert any(f.name.startswith("S-002") for f in files)


def test_new_story_fills_frontmatter(sample_project, run_agents):
    run_agents(sample_project, "new-story", "--title", "test story")
    content = (sample_project / "docs/agents/stories/S-002-test-story.md").read_text()
    assert "id: S-002" in content
    assert "status: draft" in content
    assert "title: test story" in content
    assert "## 背景" in content
    assert "## 实现日志" in content
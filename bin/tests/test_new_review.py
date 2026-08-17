"""测试 bin/agentrace new-review。"""
from pathlib import Path


def test_new_review_creates_file(sample_project, run_agents):
    result = run_agents(sample_project, "new-review", "S-001")
    assert result.returncode == 0, result.stderr
    created = sample_project / "docs/agentrace/reviews/R-001-on-S-001.md"
    assert created.exists()


def test_new_review_fills_frontmatter(sample_project, run_agents):
    run_agents(sample_project, "new-review", "S-001")
    content = (sample_project / "docs/agentrace/reviews/R-001-on-S-001.md").read_text()
    assert "story: S-001" in content
    assert "verdict: needs_discussion" in content
    assert "iteration: 1" in content


def test_new_review_requires_existing_story(sample_project, run_agents):
    result = run_agents(sample_project, "new-review", "S-999")
    assert result.returncode != 0
    assert "S-999" in result.stderr or "not found" in result.stderr.lower()
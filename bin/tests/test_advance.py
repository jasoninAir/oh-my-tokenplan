"""测试 bin/agents advance（核心状态机）。"""
import subprocess


def test_advance_draft_to_planned(sample_project, run_agents):
    """新 Story 默认 draft，可推进到 planned。"""
    run_agents(sample_project, "new-story", "--title", "draft test")
    result = run_agents(sample_project, "advance", "S-002", "planned")
    assert result.returncode == 0, result.stderr
    content = (sample_project / "docs/agents/stories/S-002-draft-test.md").read_text()
    assert "status: planned" in content


def test_advance_requires_assignee(sample_project, run_agents):
    """planned → in_progress 必须有 assignee。"""
    result = run_agents(sample_project, "advance", "S-001", "in_progress")
    assert result.returncode != 0
    assert "assignee" in result.stderr.lower()


def test_advance_planned_to_in_progress(sample_project, run_agents):
    """填 assignee 后 planned → in_progress 应成功。"""
    story = sample_project / "docs/agents/stories/S-001-test.md"
    content = story.read_text()
    content = content.replace('assignee: ""', 'assignee: "claude-impl-A"')
    story.write_text(content)

    result = run_agents(sample_project, "advance", "S-001", "in_progress")
    assert result.returncode == 0, result.stderr
    new_content = story.read_text()
    assert "status: in_progress" in new_content
    assert "planned → in_progress" in new_content


def test_advance_invalid_transition_rejected(sample_project, run_agents):
    """draft → done 应被拒绝（不允许跳级）。"""
    run_agents(sample_project, "new-story", "--title", "invalid test")
    result = run_agents(sample_project, "advance", "S-002", "done")
    assert result.returncode != 0
    assert "transition" in result.stderr.lower() or "invalid" in result.stderr.lower()
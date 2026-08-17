"""测试 bin/agents check（校验全集）。"""


def test_check_on_valid_project_passes(sample_project, run_agents):
    """sample_project 应通过 check（默认非 strict）。"""
    result = run_agents(sample_project, "check")
    assert result.returncode == 0, result.stderr


def test_check_missing_required_field_fails(tmp_path, run_agents):
    """缺必填字段时 check 应报错。"""
    stories_dir = tmp_path / "docs/agents/stories"
    stories_dir.mkdir(parents=True)
    (stories_dir / "_TEMPLATE.md").write_text("---\nid: S-NNN\n---\n")
    bad = stories_dir / "S-001-bad.md"
    bad.write_text("---\nid: S-001\nstatus: draft\n---\n## 背景\n")

    result = run_agents(tmp_path, "check", "--strict")
    assert result.returncode != 0


def test_check_unique_ids(tmp_path, run_agents):
    """重复 S-001 应报错。"""
    stories_dir = tmp_path / "docs/agents/stories"
    stories_dir.mkdir(parents=True)
    (stories_dir / "_TEMPLATE.md").write_text("---\nid: S-NNN\n---\n")
    body = (
        "---\n"
        "id: S-001\n"
        "title: dup\n"
        "status: draft\n"
        "author: x\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "---\n## 背景\n## 范围\n## 验收标准\n- [ ] x\n## 技术备注\n## 实现日志\n- x\n"
    )
    for n in ("001-a", "001-b"):
        (stories_dir / f"S-{n}.md").write_text(body)

    result = run_agents(tmp_path, "check", "--strict")
    assert result.returncode != 0
    assert "duplicate" in result.stderr.lower() or "重复" in result.stderr
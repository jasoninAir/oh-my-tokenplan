# agentrace 路线图

本季度目标：把 agentrace v0.1 从设计稿变成可运行的模板。

## 已完成

- [x] 设计 spec（2026-08-17）
- [x] AGENTS.md / CLAUDE.md / GEMINI.md
- [x] handbook 四件（story-lifecycle / review-protocol / conventions / relay-and-triage）

## 进行中

- [ ] bin/agentrace CLI 实现
- [ ] examples/calculator 完整数据
- [ ] 适配器片段 + install-snippet

## 计划中

- [ ] 自检：bin/agentrace check --strict 全通过
- [ ] 发布到 PyPI（可选）

## 阻塞

（暂无）

## 季度外

- 性能基准测试
- 类型注解覆盖率提升到 100%
- 国际化（i18n）

---

> 更新方式：完成 Story 后跑 `bin/agentrace sync`，本文件手动维护季度目标。
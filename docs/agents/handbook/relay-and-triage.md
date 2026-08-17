# 接力与事后现场勘查手册（Relay & Post-Mortem Triage）

## 1. 突发熔断痛点与设计原则

在多 Token Plan（例如 5 小时使用限额）场景下，Agent 进程可能在任意编码时刻因 API 429 报错而突然中断。由于 Agent 无法预知何时发生限额截断，系统**绝不依赖前任 Agent 的主动自知保存**，而是依赖接盘 Agent 的**事后现场勘查（Post-Mortem Triage）**。

## 2. 极速接力工作流

接手项目的 Agent 上线第一步：

```bash
bin/agents resume
# 或 bin/agents triage
```

该命令自动执行以下分析并输出 20 行极简简报：

1. **Git 差异扫描**：抓取未 commit 的 dirty 文件与暂存区修改。
2. **CodeGraph / AST 拓扑关联**：提取被修改的函数/类符号及其上下游调用方（Callers / Callees）。
3. **单测探针探测**：静默运行关联单测，抓取当前的 Failure / Error 堆栈。
4. **生成行动建议**：明确下一步最小可执行动作，避免盲读海量文件消耗 Token。

## 3. 代码影响面分析（`bin/agents impact`）

在修改核心公共接口或提交 Review 前，运行：

```bash
bin/agents impact [file_or_symbol]
```

CLI 将结合 AST / CodeGraph 输出影响拓扑，帮助 Agent 和 Reviewer 精准掌握变更波及范围。

> v0.1 实现：使用 Python `ast` 模块扫描所有 .py 文件的 `ast.FunctionDef` / `ast.ClassDef` 节点，给出定义位置 + 简单的文本调用匹配。
> v0.2 路线：真正的 AST 调用链分析（递归跟踪 `ast.Call` 节点的被调函数，处理 attr / chained / 跨文件引用），可接入外部 CodeGraph 索引（如 LSP、tree-sitter、pyright）。

## 4. 接力简报示例输出

```
==================== 现场接力简报 (Auto-Triaged) ====================
【中断任务】: S-001 (实现基础除法与异常保护)
【工作区状态】: 存在未提交修改 (Dirty Working Tree)
  - 修改文件: src/calculator/core.py (L40-L55)
【CodeGraph 语义感知】:
  - 触及符号: function `divide(a, b)`
  - 依赖影响: 2 个调用方 (tests/test_core.py, src/api/handler.py)
【测试探针当前结果】:
  - FAIL: tests/test_core.py::test_divide_by_zero (抛出 ZeroDivisionError，未封装)
  - PASS: 其余 11 个测试通过
【接力建议】:
  - 修复 core.py 中的除零捕获逻辑，使 test_divide_by_zero 转绿，提交 commit (S-001)。
========================================================================
```
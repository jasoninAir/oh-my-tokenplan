# Calculator 示例

一个 60 行的 mini Python 库，演示 agentrace的完整状态机路径。

## 怎么读这个示例

1. 从 `docs/agentrace/stories/` 开始，按 S-001 → S-002 → S-003 → S-004 顺序读
2. 对照 `docs/agentrace/reviews/` 看每一轮的反馈
3. 跑 `bin/agentrace check --strict` 验证示例数据完整
4. 对比 `src/calculator/core.py` 和 S-002 的实现日志，看返工流如何留痕

## 涵盖的状态机路径

| Story | 路径 | 演示点 |
|-------|------|--------|
| S-001 | draft → planned → in_progress → in_review → done | 一次性通过 |
| S-002 | ... → in_review → in_progress → in_review → done | 两轮 review + 返工 |
| S-003 | draft → planned | 长期 planned，验收标准留 TODO |
| S-004 | draft → planned → blocked | 卡在架构决策 |

## 运行

```bash
PYTHONPATH=src pytest -v
```

或安装后：

```bash
pip install -e .
pytest -v
```

## API

```python
from calculator import add, sub, mul, div, pow

add(1, 2).value       # 3
sub(5, 3).value       # 2
mul(3, 4).value       # 12
div(10, 2).value      # 5
pow(2, 10).value      # 1024

div(1, 0)             # raises ZeroDivisionError_
pow(2, -1)            # raises NegativeExponentError
```
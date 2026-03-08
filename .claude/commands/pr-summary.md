---
description: 为当前分支更改生成摘要
allowed-tools: Bash(git:*)
---

# PR摘要

为当前分支生成拉取请求摘要。

## 说明

1. **分析更改**：

   ```bash
   git log main..HEAD --oneline
   git diff main...HEAD --stat
   ```

2. **生成摘要**包含：
   - 更改内容的简要描述
   - 修改文件的列表
   - 破坏性更改（如果有）
   - 测试说明

3. **格式化为PR主体**：

   ```markdown
   ## 摘要

   [1-3个描述更改的项目符号]

   ## 更改

   - [重要更改的列表]

   ## 测试计划

   - [ ] [测试检查清单项目]
   ```

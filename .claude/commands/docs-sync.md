---
description: 检查文档是否与代码同步
allowed-tools: Read, Glob, Grep, Bash(git:*)
---

# 文档同步

检查文档是否与当前代码状态匹配。

## 说明

1. **查找最近的代码更改**：

   ```bash
   git log --since="30 days ago" --name-only --pretty=format: -- "*.ts" "*.tsx" | sort -u
   ```

2. **查找相关文档**：
   - 在`/docs/`中搜索提及更改代码的文件
   - 检查更改代码附近的README文件
   - 查看已更改文件中的TSDoc注释

3. **验证文档准确性**：
   - 代码示例仍然有效吗？
   - API签名正确吗？
   - Prop类型是最新的吗？

4. **仅报告实际问题**：
   - 文档是一个活文档
   - 仅标记错误的事物，而不是丢失的
   - 不要为了文档而建议文档

5. **输出需要更新的文档检查清单**

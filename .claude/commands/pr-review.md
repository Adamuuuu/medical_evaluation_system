---
description: 使用项目标准审查拉取请求
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(gh:*)
---

# PR审查

审查拉取请求：$ARGUMENTS

## 说明

1. **获取PR信息**：
   - 运行`gh pr view $ARGUMENTS`获取PR详情
   - 运行`gh pr diff $ARGUMENTS`查看更改

2. **读取审查标准**：
   - 读取`.claude/agents/code-reviewer.md`获取审查检查清单

3. **将检查清单应用**到所有更改的文件：
   - TypeScript严格模式兼容性
   - 错误处理模式
   - 加载/错误/空状态
   - 测试覆盖率
   - 文档更新

4. **提供结构化反馈**：
   - **关键**：合并前必须修复
   - **警告**：应该修复
   - **建议**：很好有

5. **发布审查评论**使用`gh pr comment`

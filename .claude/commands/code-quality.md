---
description: 在目录上运行代码质量检查
allowed-tools: Read, Glob, Grep, Bash(npm:*), Bash(npx:*)
---

# 代码质量审查

在以下目录中审查代码质量：$ARGUMENTS

## 说明

1. **识别要审查的文件**：
   - 在目录中查找所有`.ts`和`.tsx`文件
   - 排除测试文件和生成的文件

2. **运行自动化检查**：

   ```bash
   npm run lint -- $ARGUMENTS
   npm run typecheck
   ```

3. **手动审查检查清单**：
   - [ ] 没有TypeScript`any`类型
   - [ ] 正确的错误处理
   - [ ] 正确处理加载状态
   - [ ] 列表的空状态
   - [ ] Mutation有onError处理器
   - [ ] 异步操作期间按钮被禁用

4. **按严重程度报告发现**：
   - 关键（必须修复）
   - 警告（应该修复）
   - 建议（可以改进）

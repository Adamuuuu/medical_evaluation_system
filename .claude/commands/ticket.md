---
description: 端到端处理JIRA/Linear工单
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(gh:*), Bash(npm:*), mcp__jira__*, mcp__github__*, mcp__linear__*
---

# 工单工作流

处理工单：$ARGUMENTS

## 说明

### 1. 读取工单

首先，获取并理解工单：

```
使用JIRA/Linear MCP工具：
- 获取工单详情（标题、描述、验收标准）
- 检查链接的工单或epics
- 查看任何评论或附件
```

总结：

- 需要做什么
- 验收标准
- 任何阻止或依赖关系

### 2. 探索代码库

在编码前：

- 搜索相关代码
- 理解当前实现
- 识别需要更改的文件

### 3. 创建分支

```bash
git checkout -b {initials}/{ticket-id}-{brief-description}
```

### 4. 实施更改

- 遵循项目模式（检查相关技能）
- 先写测试（TDD）
- 进行增量提交

### 5. 更新工单

在工作时：

- 添加进度更新注释
- 更新状态（进行中 → 待审查）
- 记录任何阻止或问题

### 6. 创建PR并链接

准备好时：

- 使用`gh pr create`创建PR
- 将PR链接到工单
- 将工单ID添加到PR标题：`feat(PROJ-123): description`

### 7. 如果您发现Bug

如果在工作时发现无关的bug：

1. 使用详情创建新工单
2. 如果相关，将其链接到当前工单
3. 在PR描述中注明
4. 继续原始任务

## 工作流示例

```
Me: /ticket PROJ-123

Claude:
1. 从JIRA获取PROJ-123...
   标题：向个人档案页面添加用户档案头像上传
   描述：用户应该能够上传个人资料照片...
   验收标准：
   - [ ] 个人档案页面上的上传按钮
   - [ ] 支持JPG/PNG，最大5MB
   - [ ] 在上传期间显示加载状态

2. 搜索代码库中与个人档案相关的代码...
   找到：src/screens/Profile/ProfileScreen.tsx
   找到：src/components/Avatar/Avatar.tsx

3. 创建分支：cw/PROJ-123-avatar-upload

4. [使用TDD方法实施功能]

5. 将JIRA状态更新为"待审查"...
   添加评论："实施完成，PR已准备好审查"

6. 创建PR并链接到PROJ-123...
   PR #456已创建：feat(PROJ-123): 向档案添加头像上传
```

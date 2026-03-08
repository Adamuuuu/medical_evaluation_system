---
name: github-workflow
description: 用于提交、分支和PR的Git工作流代理。用于创建提交、管理分支和创建遵循项目约定的拉取请求。
model: sonnet
---

GitHub工作流助手，用于管理git操作。

## 分支命名

格式：`{initials}/{description}`

示例：

- `jd/fix-login-button`
- `jd/add-user-profile`
- `jd/refactor-api-client`

## 提交消息

使用Conventional Commits格式：

```
<type>[optional scope]: <description>

[optional body]
```

### 类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 仅文档
- `style`: 格式化，不改变代码
- `refactor`: 既不修复也不添加的代码更改
- `test`: 添加或更新测试
- `chore`: 维护任务

### 示例

```
feat(auth): 添加密码重置流程
fix(cart): 防止重复项目添加
docs(readme): 更新安装步骤
refactor(api): 提取通用获取逻辑
test(user): 添加用户档案更新测试
```

## 创建提交

1. 检查状态：

   ```bash
   git status
   git diff --staged
   ```

2. 暂存更改：

   ```bash
   git add <files>
   ```

3. 使用conventional格式创建提交：
   ```bash
   git commit -m "type(scope): description"
   ```

## 创建拉取请求

1. 推送分支：

   ```bash
   git push -u origin <branch-name>
   ```

2. 创建PR：

   ```bash
   gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
   ## 摘要
   - 更改内容的简要描述

   ## 测试计划
   - [ ] 测试通过
   - [ ] 完成手动测试
   EOF
   )"
   ```

## PR标题格式

与提交消息相同：

- `feat(auth): 添加OAuth2支持`
- `fix(api): 处理超时错误`
- `refactor(components): 简化按钮变体`

## 工作流检查清单

在创建PR前：

- [ ] 分支名称遵循约定
- [ ] 提交使用conventional格式
- [ ] 测试在本地通过
- [ ] 没有lint错误
- [ ] 更改是专注的（单一关注）

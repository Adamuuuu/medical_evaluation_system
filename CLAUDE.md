# 项目名称

> 这是一个示例CLAUDE.md文件，展示如何为你的项目配置Claude Code。

## 快速事实

- **技术栈**: React、TypeScript、Node.js
- **测试命令**: `npm test`
- **Lint命令**: `npm run lint`
- **构建命令**: `npm run build`

## 关键目录

- `src/components/` - React组件
- `src/hooks/` - 自定义React hooks
- `src/utils/` - 工具函数
- `src/api/` - API客户端代码
- `tests/` - 测试文件

## 代码风格

- TypeScript严格模式已启用
- 优先使用`interface`而非`type`（除了unions/intersections）
- 不使用`any` - 使用`unknown`替代
- 使用早期返回，避免嵌套条件
- 优先选择组合而非继承

## Git约定

- **分支命名**: `{initials}/{description}`（例如：`jd/fix-login`）
- **提交格式**: Conventional Commits（`feat:`、`fix:`、`docs:`等）
- **PR标题**: 与提交格式相同

## 关键规则

### 错误处理

- 绝对不要无声地吞掉错误
- 始终为错误显示用户反馈
- 记录错误以供调试

### UI状态

- 总是处理：加载、错误、空白、成功状态
- 仅当不存在数据时显示加载
- 每个列表都需要一个空状态

### 变更

- 在异步操作期间禁用按钮
- 在按钮上显示加载指示器
- 始终有onError处理程序和用户反馈

## 测试

- 首先编写失败的测试（TDD）
- 使用工厂模式：`getMockX(overrides)`
- 测试行为，而非实现
- 提交前运行测试

## 技能激活

在实现任何任务之前，检查是否适用相关技能：

- 创建测试 → `testing-patterns`技能
- 构建表单 → `formik-patterns`技能
- GraphQL操作 → `graphql-schema`技能
- 调试问题 → `systematic-debugging`技能
- UI组件 → `react-ui-patterns`技能

## 常见命令

```bash
# 开发
npm run dev          # 启动开发服务器
npm test             # 运行测试
npm run lint         # 运行linter
npm run typecheck    # 检查类型

# Git
npm run commit       # 交互式提交
gh pr create         # 创建PR
```

## TypeScript 类型定义示例

### 登录表单类型

遵循项目代码风格的登录表单类型定义：

```typescript
// 登录表单数据
interface LoginFormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// 登录表单状态（遵循UI状态规则）
interface LoginFormState {
  isLoading: boolean;
  error: string | null;
  data: LoginResponse | null;
}

// 登录响应
interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}
```

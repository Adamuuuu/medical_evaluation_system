# Claude Code 技能

此目录包含项目特定的技能，为Claude提供此代码库的领域知识和最佳实践。

## 按类别分类的技能

### 代码质量与模式

| 技能                                                    | 描述                                    |
| ------------------------------------------------------- | --------------------------------------- |
| [testing-patterns](./testing-patterns/SKILL.md)         | Jest测试、工厂函数、模拟策略、TDD工作流 |
| [systematic-debugging](./systematic-debugging/SKILL.md) | 四阶段调试方法论、根本原因分析          |

### React与UI

| 技能                                              | 描述                                         |
| ------------------------------------------------- | -------------------------------------------- |
| [react-ui-patterns](./react-ui-patterns/SKILL.md) | React模式、加载状态、错误处理、GraphQL hooks |
| [core-components](./core-components/SKILL.md)     | 设计系统组件、令牌、组件库                   |
| [formik-patterns](./formik-patterns/SKILL.md)     | 表单处理、验证、提交模式                     |

### 数据与API

| 技能                                        | 描述                        |
| ------------------------------------------- | --------------------------- |
| [graphql-schema](./graphql-schema/SKILL.md) | GraphQL查询、变更、代码生成 |

## 常见任务的技能组合

### 构建新特性

1. **react-ui-patterns** - 加载/错误/空状态
2. **graphql-schema** - 创建查询/变更
3. **core-components** - UI实现
4. **testing-patterns** - 编写测试（TDD）

### 构建表单

1. **formik-patterns** - 表单结构和验证
2. **graphql-schema** - 提交的变更
3. **react-ui-patterns** - 加载/错误处理

### 调试问题

1. **systematic-debugging** - 根本原因分析
2. **testing-patterns** - 首先编写失败的测试

## 技能如何工作

当Claude识别相关上下文时，技能会自动被调用。每个技能提供：

- **何时使用** - 触发条件
- **核心模式** - 最佳实践和示例
- **反模式** - 要避免的做法
- **集成** - 技能如何连接

## 添加新技能

1. 创建目录：`.claude/skills/skill-name/`
2. 添加带YAML前置的`SKILL.md`（区分大小写）：

   ```yaml
   ---
   # 必需字段
   name: skill-name # 小写、连字符、最多64个字符
   description: 它做什么以及何时使用它。包含触发关键词。 # 最多1024个字符

   # 可选字段
   allowed-tools: Read, Grep, Glob # 限制可用工具
   model: claude-sonnet-4-20250514 # 要使用的特定模型
   ---
   ```

3. 包含标准部分：何时使用、核心模式、反模式、集成
4. 添加到此README
5. 将触发器添加到`.claude/hooks/skill-rules.json`

**重要：** `description`字段至关重要—Claude使用语义匹配来决定何时应用该技能。包含用户会自然提及的关键词。

## 维护

- 当模式改变时更新技能
- 删除过时信息
- 添加新出现的模式
- 保持示例与代码库同步

# Claude Code 设置文档

## 环境变量

- `INSIDE_CLAUDE_CODE`: "1" - 表示代码在Claude Code内运行
- `BASH_DEFAULT_TIMEOUT_MS`: bash命令的默认超时时间（7分钟）
- `BASH_MAX_TIMEOUT_MS`: bash命令的最大超时时间

## Hooks

### UserPromptSubmit

- **技能评估**: 分析提示并建议相关技能
  - **脚本**: `.claude/hooks/skill-eval.sh`
  - **行为**: 匹配关键词、文件路径和模式以建议技能

### PreToolUse

- **主分支保护**: 防止在主分支上编辑（5秒超时）
  - **触发**: 在使用Edit、MultiEdit或Write工具编辑文件之前
  - **行为**: 在主分支上阻止文件编辑，建议创建特性分支

### PostToolUse

1. **代码格式化**: 自动格式化JS/TS文件（30秒超时）
   - **触发**: 在编辑`.js`、`.jsx`、`.ts`、`.tsx`文件之后
   - **命令**: `npx prettier --write`（或Biome）
   - **行为**: 格式化代码，如果发现错误则显示反馈

2. **NPM安装**: package.json更改后自动安装（60秒超时）
   - **触发**: 在编辑`package.json`文件之后
   - **命令**: `npm install`
   - **行为**: 安装依赖，如果安装失败则编辑失败

3. **测试运行器**: 测试文件更改后运行测试（90秒超时）
   - **触发**: 在编辑`.test.js`、`.test.jsx`、`.test.ts`、`.test.tsx`文件之后
   - **命令**: `npm test -- --findRelatedTests <file> --passWithNoTests`
   - **行为**: 运行相关测试，显示结果，非阻塞

4. **TypeScript检查**: TS/TSX文件类型检查（30秒超时）
   - **触发**: 在编辑`.ts`、`.tsx`文件之后
   - **命令**: `npx tsc --noEmit`
   - **行为**: 仅显示首个错误，非阻塞

## Hook响应格式

```json
{
  "feedback": "要显示的消息",
  "suppressOutput": true,
  "block": true,
  "continue": false
}
```

## Hook中的环境变量

- `$CLAUDE_TOOL_INPUT_FILE_PATH`: 正在编辑的文件
- `$CLAUDE_TOOL_NAME`: 正在使用的工具
- `$CLAUDE_PROJECT_DIR`: 项目根目录

## 退出码

- `0`: 成功
- `1`: 非阻塞错误（显示反馈）
- `2`: 阻塞错误（仅限PreToolUse - 阻止操作）

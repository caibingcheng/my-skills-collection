# 验证工作流指南

本文件描述任务验证的完整工作流和最佳实践。

## 验证原则

**核心原则：先验证，后声明完成**

任何任务在声明完成前，必须经过实际验证。不要依赖于"应该可以"或"看起来正确"的假设。

## 验证工作流程

### 步骤1：确定验证需求

根据任务类型确定需要验证的内容：

| 任务类型 | 验证内容 |
|---------|---------|
| 生成脚本 | 脚本是否可执行、输出是否符合预期 |
| 代码更改 | 编译是否正常、测试是否通过 |
| 配置文件 | 配置是否有效、格式是否正确 |
| 文档编写 | 链接是否有效、内容是否正确 |
| 数据库迁移 | 迁移是否成功、数据是否一致 |
| API实现 | 端点是否可达、响应是否正确 |

### 步骤2：评估验证环境影响

**关键问题：** 这个验证会影响当前环境吗？

需要评估的情况：
- 运行脚本是否会更改文件系统？
- 测试是否会修改数据库？
- 编译是否会产生副作用？
- 执行是否会消耗大量资源？

如果答案为"是"，则必须使用隔离环境进行验证。

### 步骤3：选择验证方法

**方法A：直接验证**
- 适用于：只读操作、无副作用的验证
- 示例：语法检查、静态分析、文档链接检查

**方法B：虚拟环境验证**
- 适用于：Python脚本、Node.js项目
- 工具：venv、virtualenv、conda
- 优点：隔离依赖、不影响系统Python

**方法C：容器验证**
- 适用于：需要完整系统环境的验证
- 工具：Docker、Podman
- 优点：完全隔离、可重现

### 步骤4：执行验证

#### 脚本验证

```python
# 使用 verify_script.py
python scripts/verify_script.py my_script.py --expected-output "success" --json
```

检查点：
- [ ] 文件存在
- [ ] 具有执行权限
- [ ] Shebang正确（如果是脚本）
- [ ] 返回码符合预期
- [ ] 输出内容符合预期

#### 编译验证

```python
# 使用 verify_build.py
python scripts/verify_build.py /path/to/project --json
```

检查点：
- [ ] 检测到正确的项目类型
- [ ] 依赖安装成功
- [ ] 编译/构建成功
- [ ] 测试通过（如果有）

#### 容器验证

```python
# 创建隔离环境
python scripts/manage_venv.py create --type docker --image python:3.11-slim

# 在容器中验证
python scripts/manage_venv.py run --container <id> -- python my_script.py
```

### 步骤5：分析验证结果

**验证通过：**
- 所有检查点通过
- 没有错误
- 可以声明任务完成

**验证失败：**
- 记录具体错误
- 修复问题
- 重新验证

**验证部分通过（有警告）：**
- 评估警告的严重性
- 决定是否可以接受
- 文档化已知问题

## 常见验证场景

### 场景1：Python脚本生成

```bash
# 1. 创建虚拟环境
python scripts/manage_venv.py create --type venv --name test-env

# 2. 在虚拟环境中验证
python scripts/manage_venv.py run --venv test-env -- python generated_script.py

# 3. 使用验证脚本
python scripts/verify_script.py generated_script.py --expected-output "completed"
```

### 场景2：项目构建

```bash
# 自动检测项目类型并验证
python scripts/verify_build.py ./my-project
```

### 场景3：复杂系统验证

```bash
# 1. 创建Docker容器
python scripts/manage_venv.py create --type docker --image ubuntu:22.04

# 2. 在容器中执行完整验证流程
python scripts/manage_venv.py run --container <id> -- bash -c "
    apt-get update && apt-get install -y python3
    python3 /app/verify.py
"
```

## 验证报告格式

验证完成后应生成结构化报告：

```json
{
  "task": "脚本生成",
  "verified": true,
  "method": "venv",
  "checks": {
    "syntax": true,
    "execution": true,
    "output": true
  },
  "errors": [],
  "warnings": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 反模式

**❌ 不要做的：**
1. 依赖代码审查代替实际验证
2. 说"应该可以"而不实际运行
3. 只在本地验证，不考虑环境差异
4. 忽略验证中的警告
5. 使用生产环境进行验证

**✅ 应该做的：**
1. 始终先验证再声明完成
2. 使用隔离环境进行有风险的操作
3. 记录验证过程和结果
4. 对于复杂场景，使用多种验证方法
5. 自动化重复验证任务

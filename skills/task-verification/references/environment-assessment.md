# 环境评估指南

本文件描述如何评估验证环境并选择合适的隔离策略。

## 环境评估检查清单

### 基础评估

1. **任务类型分析**
   - 生成内容：代码、脚本、配置文件
   - 修改内容：现有文件、数据库、系统配置
   - 纯分析：静态检查、代码审查、文档验证

2. **潜在影响评估**
   - 文件系统：是否会创建/修改/删除文件？
   - 网络：是否会发起网络请求？
   - 资源：是否会占用大量CPU/内存/磁盘？
   - 持久化：是否会修改数据库或配置？

3. **依赖评估**
   - Python包：是否需要安装额外依赖？
   - 系统工具：是否需要特定系统软件？
   - 服务依赖：是否需要数据库、缓存等服务？

### 风险等级划分

#### 低风险（可直接验证）

- 纯读取操作
- 静态代码分析
- 文档链接检查
- 语法检查（不执行）

#### 中风险（建议使用venv）

- Python脚本执行
- Node.js脚本运行
- 依赖安装和测试
- 文件生成（在临时目录）

#### 高风险（必须使用容器）

- 系统级更改
- 需要root权限的操作
- 网络服务启动
- 数据库操作
- 可能影响宿主机的编译

## 隔离策略选择矩阵

| 任务特征 | 推荐策略 | 工具 |
|---------|---------|-----|
| Python脚本验证 | Python venv | `python -m venv` |
| Node.js项目 | npm + 临时目录 | `npm install` in tmp |
| 多语言项目 | Docker容器 | Docker/Podman |
| 快速验证 | 临时目录 | `tempfile` |
| 完整系统测试 | 完整容器 | Docker + Compose |

## 环境检测流程

```python
# 使用 manage_venv.py 检测可用工具
python scripts/manage_venv.py detect
```

输出示例：
```json
{
  "python_venv": true,
  "docker": true,
  "podman": false
}
```

基于检测结果选择策略：
- 如果 `python_venv` 可用 → 优先使用venv
- 如果 `docker` 可用 → 用于高风险操作
- 如果都不可用 → 使用临时目录（有限隔离）

## 环境创建最佳实践

### Python venv

**适用场景：**
- Python脚本验证
- 需要特定Python版本
- 依赖隔离

**创建命令：**
```bash
python scripts/manage_venv.py create --type venv --name verify-env
```

**生命周期：**
1. 创建venv
2. 安装依赖（如需要）
3. 执行验证
4. 清理venv

### Docker容器

**适用场景：**
- 需要完整Linux环境
- 多语言项目
- 高隔离要求

**创建命令：**
```bash
python scripts/manage_venv.py create --type docker --image python:3.11-slim
```

**最佳实践：**
- 使用官方基础镜像
- 保持容器轻量
- 使用卷挂载共享文件
- 及时清理不再使用的容器

### Podman容器

**适用场景：**
- 无root权限运行容器
- 与Docker兼容但更安全的场景

**创建命令：**
```bash
python scripts/manage_venv.py create --type podman --image python:3.11-slim
```

## 验证环境准备检查清单

在启动验证前，确认以下事项：

### venv环境
- [ ] 确认Python版本符合要求
- [ ] 检查venv创建是否成功
- [ ] 验证pip可用
- [ ] 如需要，安装requirements

### Docker环境
- [ ] 确认Docker服务运行
- [ ] 检查镜像是否可拉取
- [ ] 确认磁盘空间充足
- [ ] 设置适当的资源限制

### 通用检查
- [ ] 确认验证脚本可访问
- [ ] 准备测试数据（如需要）
- [ ] 设置超时时间
- [ ] 确认输出目录可写

## 环境恢复策略

### 自动清理

所有验证脚本都支持自动清理：

```python
# 创建时指定自动清理
manager = VirtualEnvManager()
manager.create_python_venv()
# 使用完毕自动调用 manager.cleanup()
```

### 手动清理

```bash
# 清理venv
python scripts/manage_venv.py cleanup --path /path/to/venv

# 清理Docker容器
docker rm -f <container_id>
```

### 故障恢复

如果验证中断：
1. 检查遗留的临时文件
2. 清理未完成的容器
3. 重置venv状态（如需要）
4. 重新运行验证

## 性能考虑

### 启动时间
- venv: 数秒
- Docker容器: 数秒到数十秒（取决于镜像大小）
- Podman: 类似Docker

### 资源占用
- venv: 磁盘空间（Python安装+依赖）
- Docker: 磁盘 + 内存（容器运行时）
- Podman: 类似Docker

### 优化建议
- 对于频繁验证，保持venv复用
- 使用多阶段构建减小Docker镜像
- 考虑使用Docker层缓存
- 对于CI/CD，使用预构建镜像

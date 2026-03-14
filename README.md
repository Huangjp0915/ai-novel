# 📚 AI小说连载生成系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local-orange.svg)

**基于本地大语言模型的多Agent协作小说生成系统，支持百万字长篇连载**

[功能特性](#-核心功能) • [快速开始](#-快速开始) • [项目优势](#-项目优势) • [技术架构](#-技术架构)

</div>

---

## ✨ 核心功能

### 🎯 多Agent协作系统
- **Radar（雷达）**: 扫描平台趋势和读者偏好，指导故事方向
- **Architect（建筑师）**: 规划章节结构、场景节拍、节奏控制
- **Writer（写手）**: 根据大纲和世界状态生成正文
- **Auditor（审计员）**: 26维度内容审计，确保质量
- **Reviser（修订者）**: 自动修复审计发现的问题
- **Continuity Guard（连续性守卫）**: 检查角色一致性、时间线、世界观冲突
- **Ledger Updater（账本更新器）**: 智能更新长期记忆文件
- **Arc Reviewer（弧线审查员）**: 每10-20章进行弧线审查

### 📖 智能大纲生成
- **总纲生成**: 根据设定自动生成完整的故事总纲
- **卷纲生成**: 基于总纲生成各卷详细规划
- **细纲生成**: 为每一章生成详细的写作大纲
- **一致性检查**: 自动检查大纲与设定的冲突

### 🧠 长期记忆系统（16个Memory文件）
- `current_state.md` - 世界状态：角色位置、关系网络、已知信息
- `particle_ledger.md` - 资源账本：物品、金钱、物资数量追踪
- `pending_hooks.md` - 未闭合伏笔：铺垫、承诺、未解决冲突
- `chapter_summaries.md` - 章节摘要：出场人物、关键事件、状态变化
- `subplot_board.md` - 支线进度板：A/B/C线状态、停滞检测
- `emotional_arcs.md` - 情感弧线：按角色追踪情绪变化和成长
- `character_matrix.md` - 角色交互矩阵：相遇记录、信息边界
- `爽点规划.md` - 爽点规划
- `世界观.md` - 世界观设定
- `主角卡.md` - 主角设定
- `主角组.md` - 主角团队设定
- `力量体系.md` - 力量体系设定
- `反派设计.md` - 反派设定
- `复合题材-融合逻辑.md` - 题材融合逻辑
- `女主卡.md` - 女主设定
- `金手指设计.md` - 金手指设定

### 🔍 26维度审计系统
- **OOC检查**: 角色行为一致性
- **时间线检查**: 时间逻辑一致性
- **设定冲突**: 世界观规则冲突检测
- **伏笔管理**: 伏笔铺设与回收检查
- **节奏控制**: 章节节奏分析
- **文风检查**: 文风一致性
- **信息越界**: 角色信息边界检查
- **词汇疲劳**: 重复词汇检测
- **AI痕迹检测**: 自动识别AI生成特征（维度20-23纯规则引擎）
- **去AI味规则**: 5条通用规则 + 题材专属语言规则

### 🌐 Web界面
- **项目管理**: 创建、选择、管理多个小说项目
- **设定编辑**: 可视化编辑所有Memory文件
- **大纲管理**: 生成、查看、编辑总纲、卷纲、细纲
- **章节生成**: 从细纲中选择章节进行生成
- **配置管理**: 支持多AI平台配置（Ollama、OpenAI、Anthropic等）

### 📁 多项目支持
- 支持同时管理多个小说项目
- 每个项目独立的数据存储
- 项目间完全隔离

---

## 🚀 项目优势

### 相比其他AI小说生成项目的优势

1. **🎯 专业的多Agent协作架构**
   - 不是简单的单次LLM调用，而是5-8个专业Agent协作
   - 每个Agent专注于特定任务，确保专业性和质量
   - 完整的审计-修订循环，确保输出质量

2. **🧠 强大的长期记忆系统**
   - 16个结构化Memory文件，远超其他项目的简单上下文
   - 智能的账本更新系统，支持冲突检测和版本管理
   - 支持百万字长篇连载，不会出现前后矛盾

3. **🔍 业界领先的26维度审计系统**
   - 不仅检查内容质量，还检查AI痕迹
   - 规则引擎 + LLM双重检测，确保准确性
   - 自动修复机制，减少人工干预

4. **📖 完整的大纲生成体系**
   - 总纲 → 卷纲 → 细纲的三级大纲体系
   - 自动一致性检查，防止设定冲突
   - 支持可视化编辑和修改

5. **🌐 现代化的Web界面**
   - 直观的可视化操作界面
   - 支持实时编辑和预览
   - 多项目管理，无需命令行操作

6. **🔧 灵活的AI平台支持**
   - 支持本地部署（Ollama）
   - 支持云端API（OpenAI、Anthropic等）
   - 可随时切换AI平台

7. **💾 完善的版本管理**
   - 自动备份Memory文件
   - 版本历史记录
   - 支持回滚操作

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Web界面 (Flask)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │项目管理  │  │设定编辑  │  │大纲管理  │  │章节生成  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               ChapterWorkflow (工作流)                   │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Radar │→ │Arch  │→ │Writer│→ │Audit │→ │Revise│    │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘    │
│                          │                              │
│                          ▼                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │Continuity    │  │Ledger        │  │Arc           │ │
│  │Guard         │  │Updater       │  │Reviewer      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            FileManager (文件管理系统)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │Memory Files  │  │Chapter Files │  │Config Files  │ │
│  │(16个文件)    │  │(章节正文)    │  │(配置规则)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            OllamaClient (AI客户端)                      │
│             支持本地和云端AI平台                         │
└─────────────────────────────────────────────────────────┘
```

### 核心技术栈

- **后端框架**: Flask 3.0+
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **AI平台**: Ollama (本地) / OpenAI / Anthropic / DeepSeek等
- **数据存储**: 文件系统 (Markdown格式)
- **版本管理**: 自定义版本管理系统

---

## 🚀 快速开始

### 前置要求

- **Python**: 3.8 或更高版本
- **GPU**: RTX 5090（推荐）或同等算力（运行30B+模型）
- **内存**: 32GB+（运行30B模型）
- **磁盘空间**: 至少50GB（用于模型和项目文件）

### 第一步：安装Ollama

#### Windows系统

1. 访问 [Ollama官网](https://ollama.com/download) 下载Windows安装包
2. 运行安装程序，按照提示完成安装
3. 验证安装：
   ```bash
   ollama --version
   ```

#### Linux/Mac系统

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Mac
brew install ollama
```

### 第二步：下载AI模型

```bash
# 下载Qwen3:30b模型（推荐，中文能力强）
ollama pull qwen3:30b

# 或者下载其他模型
ollama pull qwen2.5:32b      # 更小的模型，适合显存不足
ollama pull llama3:70b       # 更大的模型，需要更多显存

# 验证模型已下载
ollama list
```

**注意**: 30B模型需要约60GB显存，请根据您的硬件选择合适的模型。

### 第三步：克隆项目

```bash
# 使用Git克隆
git clone https://github.com/your-username/ai-novel.git
cd ai-novel

# 或者直接下载ZIP文件并解压
```

### 第四步：创建Python虚拟环境

#### Windows系统

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 验证激活成功（命令行前应显示(venv)）
```

#### Linux/Mac系统

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证激活成功（命令行前应显示(venv)）
```

### 第五步：安装Python依赖

```bash
# 确保虚拟环境已激活
# 升级pip到最新版本
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list
```

**依赖说明**:
- `requests`: HTTP请求库，用于调用Ollama API
- `python-dotenv`: 环境变量管理
- `flask`: Web框架
- `flask-cors`: 跨域支持

### 第六步：配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，配置以下内容：

```env
# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b

# 项目配置
PROJECT_ROOT=./projects
CHAPTER_TARGET_WORDS=3000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/ai_novel.log
```

### 第七步：启动Ollama服务

```bash
# 如果Ollama未自动启动，手动启动
ollama serve

# 保持此终端窗口打开，不要关闭
```

**验证Ollama运行**:
- 打开浏览器访问: http://localhost:11434
- 应该能看到Ollama的API文档页面

### 第八步：启动Web界面

```bash
# 确保虚拟环境已激活
# 确保Ollama服务正在运行

# 启动Web应用
python app.py
```

**启动成功标志**:
```
============================================================
AI小说连载系统 - Web界面
============================================================

访问地址: http://127.0.0.1:5000

按 Ctrl+C 停止服务器
============================================================
```

### 第九步：访问Web界面

1. 打开浏览器，访问: http://127.0.0.1:5000
2. 您将看到AI小说系统的Web界面

---

## 📖 使用指南

### 创建第一个项目

1. **打开Web界面**: 访问 http://127.0.0.1:5000
2. **创建项目**: 
   - 点击左侧"项目管理"
   - 点击"创建新项目"按钮
   - 输入项目名称（如：我的第一本小说）
   - 选择题材（如：玄幻、都市异能等）
   - 点击"创建"

3. **填写设定文件**:
   - 点击左侧"设定编辑"
   - 在左侧文件列表中选择要编辑的文件
   - 在右侧编辑器中填写内容
   - 点击"保存"按钮保存

**重要设定文件**:
- `世界观.md`: 描述小说的世界观设定
- `主角卡.md`: 主角的详细设定
- `力量体系.md`: 力量体系的设定
- `爽点规划.md`: 爽点的规划

### 生成大纲

1. **生成总纲**:
   - 点击左侧"大纲管理"
   - 切换到"总纲"标签页
   - 点击"生成总纲"按钮
   - 输入目标总字数（如：1000000）
   - 等待生成完成
   - 可以点击编辑器直接修改总纲内容
   - 点击"保存总纲"保存修改

2. **生成卷纲**:
   - 切换到"卷纲"标签页
   - 点击"生成卷纲"按钮
   - 输入卷号（如：1）
   - 等待生成完成
   - 可以编辑和保存卷纲

3. **生成细纲**:
   - 切换到"细纲"标签页
   - 从下拉框选择卷号
   - 点击"生成细纲"按钮
   - 输入章节编号（如：1）
   - 等待生成完成
   - 可以编辑和保存细纲

### 生成章节

1. **选择章节**:
   - 点击左侧"章节生成"
   - 从"卷号"下拉框选择卷号
   - 系统会显示该卷所有已有细纲的章节
   - 点击要生成的章节卡片

2. **生成章节**:
   - 确认"已选章节"显示正确
   - 点击"生成章节"按钮
   - 等待生成完成（可能需要几分钟）
   - 生成完成后会自动显示章节内容

3. **查看章节**:
   - 章节文件保存在: `projects/[项目ID]/chapters/chapter_XXX.md`
   - 可以在Web界面直接查看
   - 也可以使用文本编辑器打开

### 配置AI平台

1. **访问配置页面**:
   - 点击左侧"配置管理"

2. **切换AI平台**:
   - 从"当前AI平台"下拉框选择平台
   - 填写该平台的配置信息
   - 配置会自动保存

3. **支持的平台**:
   - **Ollama** (本地): 无需API Key
   - **OpenAI**: 需要API Key
   - **Anthropic (Claude)**: 需要API Key
   - **DeepSeek**: 需要API Key
   - **通义千问**: 需要API Key
   - **智谱AI**: 需要API Key

---

## 📁 项目结构

```
ai-novel/
├── agents/                      # Agent实现
│   ├── base_agent.py           # Agent基类
│   ├── radar.py                # Radar Agent
│   ├── architect.py            # Architect Agent
│   ├── writer.py               # Writer Agent
│   ├── auditor.py              # Auditor Agent
│   ├── reviser.py              # Reviser Agent
│   ├── continuity_guard.py    # Continuity Guard
│   ├── ledger_updater.py       # Ledger Updater
│   ├── arc_reviewer.py         # Arc Reviewer
│   ├── outline_generator.py    # 大纲生成Agent
│   └── outline_checker.py      # 大纲检查Agent
├── utils/                       # 工具模块
│   ├── ollama_client.py        # Ollama客户端
│   ├── file_manager.py         # 文件管理
│   ├── project_manager.py      # 项目管理
│   ├── outline_manager.py      # 大纲管理
│   ├── ai_config.py            # AI配置管理
│   └── ledger_version_manager.py  # 版本管理
├── config/                      # 配置文件
│   ├── genre_rules/            # 题材规则
│   ├── audit_dimensions.md     # 审计维度
│   ├── consistency_rules.md   # 一致性规则
│   └── platform_styles.md     # 平台风格
├── templates/                   # HTML模板
│   └── index.html              # 主页面
├── static/                      # 静态资源
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── js/
│       └── app.js              # 前端逻辑
├── projects/                    # 项目存储目录
│   └── [项目ID]/
│       ├── memory/             # Memory文件
│       ├── chapters/           # 生成的章节
│       ├── outlines/           # 大纲文件
│       ├── config/             # 项目配置
│       └── logs/               # 日志文件
├── app.py                       # Web应用入口
├── main.py                      # 命令行入口
├── workflow.py                  # 工作流实现
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
└── README.md                    # 项目说明
```

---

## 🔧 常见问题

### Q: Ollama连接失败怎么办？

**A**: 检查以下几点：
1. 确认Ollama服务正在运行: `ollama serve`
2. 检查端口11434是否被占用
3. 确认`.env`文件中的`OLLAMA_BASE_URL`配置正确
4. 尝试访问 http://localhost:11434 查看是否正常

### Q: 模型下载很慢怎么办？

**A**: 
1. 使用国内镜像源（如果有）
2. 选择更小的模型（如qwen2.5:32b）
3. 使用代理加速下载

### Q: 生成章节时显存不足？

**A**:
1. 使用更小的模型（如qwen2.5:32b）
2. 减少`max_tokens`参数
3. 关闭其他占用显存的程序

### Q: 如何切换AI平台？

**A**:
1. 打开Web界面
2. 点击"配置管理"
3. 选择要使用的平台
4. 填写配置信息（如API Key）
5. 配置会自动保存并生效

### Q: 项目文件在哪里？

**A**: 
- 所有项目文件存储在`projects/`目录下
- 每个项目有独立的文件夹
- 章节文件在`projects/[项目ID]/chapters/`目录

### Q: 如何备份项目？

**A**:
1. 直接复制`projects/[项目ID]`文件夹
2. 或者使用Git版本控制
3. Memory文件有自动版本备份功能

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- 使用Python类型提示
- 遵循PEP 8代码风格
- 添加必要的注释和文档字符串
- 确保代码通过lint检查

---

## 📝 更新日志

### v1.0.0 (2024-03-14)
- ✨ 初始版本发布
- ✨ 多Agent协作系统
- ✨ 16个Memory文件支持
- ✨ 26维度审计系统
- ✨ Web界面
- ✨ 多项目支持
- ✨ 大纲生成系统

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [Ollama](https://ollama.com/) - 本地大模型运行环境
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Qwen](https://github.com/QwenLM/Qwen) - 优秀的中文大语言模型

---

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/Huangjp0915/ai-novel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Huangjp0915/ai-novel/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请给一个 ⭐ Star！**

Made with ❤️ by AI Novel Team

</div>

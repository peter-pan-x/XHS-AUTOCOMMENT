# 小红书自动评论工具 V5

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

一个基于 Selenium 和 undetected-chromedriver 的小红书自动评论脚本,通过模拟真实用户行为实现自动化评论功能。

[功能特性](#功能特性) • [快速开始](#快速开始) • [配置说明](#配置说明) • [使用方法](#使用方法) • [注意事项](#注意事项)

</div>

---

## 📋 目录

- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [文件说明](#文件说明)
- [注意事项](#注意事项)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [许可证](#许可证)

---

## ✨ 功能特性

### V5.1 版本新增功能

- ✅ **图形化配置面板** - 简单易用的 GUI 界面,无需手动编辑配置文件
- ✅ **实时风险提示** - 根据配置自动显示风险等级
- ✅ **评论库管理** - 可视化添加、编辑、删除评论内容

### V5.0 版本新增功能

- ✅ **启动时自动清理 Chrome 进程** - 避免进程冲突导致脚本失败
- ✅ **SQLite 数据库记录** - 自动记录已评论的笔记,防止重复评论
- ✅ **自动日志导出** - 完整记录运行过程和统计信息
- ✅ **配置文件分离** - 独立的 `config.py`,便于维护和修改

### 核心功能

- 🔐 **智能登录管理** - Cookie 持久化,免重复登录
- 🤖 **反检测机制** - 使用 undetected-chromedriver 绕过 Selenium 检测
- 🎯 **关键词搜索** - 根据配置的关键词自动搜索笔记
- 💬 **随机评论** - 从评论列表中随机选择,避免连续重复
- 🎭 **人类行为模拟** - 随机延迟、平滑滚动、逐字输入
- 🛡️ **风控检测** - 自动检测风控提示并跳过
- 📊 **运行统计** - 显示成功、失败、跳过的详细统计
- 📝 **完整日志** - 实时日志输出和文件导出

---

## 🏗️ 技术架构

### 核心技术栈

- **undetected-chromedriver** - 反检测浏览器驱动
- **Selenium** - 浏览器自动化框架
- **SQLite** - 本地数据库存储
- **Python 3.8+** - 编程语言

### 代码结构

```
xiaohongshu_auto_comment_v5.py (主程序)
├── Logger 类 (日志管理)
├── CommentDatabase 类 (数据库管理)
├── XHSBot 类 (核心业务逻辑)
│   ├── init_driver() - 初始化浏览器
│   ├── search_keyword() - 搜索关键词
│   ├── get_note_links() - 获取笔记列表
│   ├── open_note() - 打开笔记
│   ├── post_comment() - 发布评论
│   ├── close_note() - 关闭笔记
│   └── run() - 主运行流程
└── 辅助函数 (进程管理、Cookie 管理、风控检测等)

config.py (配置文件)
└── Config 类 (所有配置参数)
```

---

## 💻 环境要求

### 系统要求

- **操作系统**: Windows 10/11 (推荐)
- **Python 版本**: Python 3.8 或更高版本
- **浏览器**: Google Chrome 浏览器

### Python 依赖

- `undetected-chromedriver >= 3.5.0`
- `selenium >= 4.15.0`

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/peter-pan-x/XHS-AUTOCOMMENT.git
cd XHS-AUTOCOMMENT
```

### 2. 安装依赖

**方法一: 使用一键安装脚本 (推荐)**

```bash
# Windows 系统
双击运行 install_dependencies.bat
```

**方法二: 手动安装**

```bash
pip install -r requirements.txt
```

### 3. 准备 ChromeDriver

- 下载与您的 Chrome 浏览器版本匹配的 ChromeDriver
- 下载地址: [ChromeDriver 官网](https://chromedriver.chromium.org/downloads)
- 将 `chromedriver.exe` 放置在脚本同目录下

> **提示**: 查看 Chrome 版本: 打开 Chrome 浏览器 → 右上角三个点 → 帮助 → 关于 Google Chrome

### 4. 修改配置

**方法一: 使用图形化配置面板 (推荐,适合小白)**

```bash
# Windows 系统
双击运行: 启动配置面板.bat

# 或命令行启动
python config_gui.py
```

在配置面板中可以轻松设置:
- 搜索关键词
- 评论数量和间隔
- 评论内容库管理(添加/编辑/删除)
- 实时风险提示

**方法二: 手动编辑配置文件**

编辑 `config.py` 文件,修改以下参数:

```python
# 搜索关键词
SEARCH_KEYWORD = "你的关键词"

# 评论内容列表
COMMENTS = [
    "评论内容1",
    "评论内容2",
    "评论内容3",
    # ... 更多评论
]

# 目标评论数量
NOTES_TO_COMMENT = 5

# 评论间隔时间 (秒)
MIN_INTERVAL = 55
```

### 5. 运行脚本

```bash
python xiaohongshu_auto_comment_v5.py
```

### 6. 首次运行

- 脚本会自动打开浏览器
- 如果未登录,请在 **55 秒**内完成扫码登录
- 登录后可以随意浏览几个笔记(预热账号)
- 登录状态会自动保存,下次运行无需重复登录

---

## ⚙️ 配置说明

### 主要配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SEARCH_KEYWORD` | "玉灵膏" | 搜索关键词 |
| `NOTES_TO_COMMENT` | 3 | 目标评论数量 |
| `MIN_INTERVAL` | 55 秒 | 每次评论之间的最小间隔 |
| `PREHEAT_TIMEOUT` | 55 秒 | 预热等待时间(登录和浏览) |
| `COMMENTS` | 20 条 | 评论内容列表 |
| `COOKIE_FILE` | "xhs_cookies.pkl" | Cookie 保存文件名 |
| `DATABASE_FILE` | "xhs_commented_notes.db" | 数据库文件名 |
| `LOG_FILE` | "xhs_auto_comment_log.txt" | 日志文件名 |

### 安全参数建议

根据账号类型和使用场景,建议使用以下配置:

| 风险等级 | 每次评论数 | 适用场景 |
|---------|-----------|---------|
| 🟢 极低风险 | 3-5 条 | 新账号、谨慎使用 |
| 🟡 低风险 | 5-8 条 | 正常账号、日常使用 |
| 🟠 中风险 | 8-12 条 | 老账号、偶尔使用 |
| 🔴 高风险 | 12 条以上 | 不建议 |

**推荐配置**: 每次 3-5 条,间隔 55 秒以上

**每天运行频率建议**:

| 账号类型 | 每天运行次数 | 总评论数/天 | 时间间隔 |
|---------|------------|-----------|---------|
| 🆕 新账号 (< 1个月) | 1-2 次 | 5-10 条 | 间隔 4-6 小时 |
| 📱 普通账号 (1-6个月) | 2-3 次 | 10-15 条 | 间隔 3-5 小时 |
| 👑 老账号 (> 6个月) | 3-4 次 | 15-20 条 | 间隔 2-4 小时 |

---

## 📖 使用方法

### 基本使用

1. **修改配置文件** (`config.py`)
   - 设置搜索关键词
   - 配置评论内容列表
   - 调整评论数量和间隔时间

2. **运行脚本**
   ```bash
   python xiaohongshu_auto_comment_v5.py
   ```

3. **首次运行登录**
   - 脚本会自动打开浏览器
   - 在 55 秒内完成扫码登录
   - 可以随意浏览几个笔记

4. **自动评论**
   - 脚本会自动搜索关键词
   - 按顺序打开笔记
   - 随机选择评论内容
   - 自动发布评论
   - 记录到数据库

5. **查看结果**
   - 控制台会显示实时进度
   - 任务完成后显示统计信息
   - 日志文件: `xhs_auto_comment_log.txt`

### 高级使用

#### 检查依赖

```bash
# Windows 系统
双击运行 check_dependencies.bat
```

#### 清理数据

如果需要重新评论已评论过的笔记:

```bash
# 删除数据库文件
del xhs_commented_notes.db

# 删除 Cookie 文件 (需要重新登录)
del xhs_cookies.pkl
```

#### 查看日志

每次运行都会生成日志文件,包含:
- 每个操作的时间戳
- 成功/失败状态
- 错误信息和堆栈跟踪
- 完整的运行轨迹

---

## 📁 文件说明

### 核心文件

| 文件名 | 说明 |
|--------|------|
| `xiaohongshu_auto_comment_v5.py` | 主程序文件 |
| `config.py` | 配置文件 |
| `config_gui.py` | 图形化配置面板 |
| `requirements.txt` | Python 依赖列表 |
| `README.md` | 项目说明文档 |

### 辅助文件

| 文件名 | 说明 |
|--------|------|
| `启动配置面板.bat` | 一键启动配置面板 |
| `install_dependencies.bat` | 一键安装依赖脚本 |
| `check_dependencies.bat` | 检查依赖是否安装 |
| `LICENSE.chromedriver` | ChromeDriver 许可证 |
| `THIRD_PARTY_NOTICES.chromedriver` | 第三方声明 |
| `配置面板使用说明.md` | 配置面板详细说明 |
| `docs/小红书自动评论脚本_V5_-_优化版.pdf` | 详细使用文档 |

### 运行时生成的文件

| 文件名 | 说明 | 是否可删除 |
|--------|------|----------|
| `xhs_cookies.pkl` | Cookie 持久化文件 | 可删除(需重新登录) |
| `xhs_commented_notes.db` | 已评论笔记数据库 | 可删除(会重复评论) |
| `xhs_auto_comment_log.txt` | 运行日志文件 | 可删除 |
| `AutomationProfile/` | 浏览器用户数据目录 | 可删除 |

---

## ⚠️ 注意事项

### 合理使用

1. **时间间隔**
   - 不要设置过短的时间间隔(建议 ≥ 45 秒)
   - 不要一次性评论太多(建议 ≤ 10 条)

2. **评论内容**
   - 评论内容要多样化,避免重复
   - 避免敏感词汇和广告内容
   - 尽量使用自然、真实的评论

3. **账号安全**
   - 建议使用真实账号,并保持正常使用习惯
   - 可以适当增加 `MIN_INTERVAL` 间隔时间
   - 避免长时间连续运行

### 风控问题

如果遇到验证码或风控提示:
- 脚本会自动跳过
- 建议停止运行,等待一段时间
- 可以手动登录浏览几个笔记
- 适当增加 `MIN_INTERVAL` 间隔时间

### 数据管理

1. **评论记录数据库**
   - `xhs_commented_notes.db` 会持续累积记录
   - 如需重新评论已评论笔记,可删除此文件
   - 建议定期备份该文件

2. **日志文件**
   - 日志文件会持续累积,建议定期清理
   - 每次运行都会生成新的日志文件
   - 可通过日志文件追溯历史运行情况

### 法律声明

- 本工具仅供学习和研究使用
- 请遵守小红书平台规则和相关法律法规
- 使用本工具产生的任何后果由使用者自行承担
- 不得用于商业用途或非法用途

---

## ❓ 常见问题

### 1. 脚本无法启动?

**可能原因**:
- Python 版本过低(需要 3.8+)
- 依赖未安装
- ChromeDriver 未找到或版本不匹配

**解决方法**:
```bash
# 检查 Python 版本
python --version

# 重新安装依赖
pip install -r requirements.txt

# 检查 ChromeDriver 是否存在
dir chromedriver.exe
```

### 2. 浏览器无法打开?

**可能原因**:
- ChromeDriver 版本与 Chrome 浏览器版本不匹配
- Chrome 进程残留

**解决方法**:
- 下载匹配版本的 ChromeDriver
- 手动关闭所有 Chrome 进程
- 脚本会在启动时自动清理进程

### 3. 登录状态丢失?

**可能原因**:
- Cookie 文件被删除
- Cookie 过期

**解决方法**:
- 删除 `xhs_cookies.pkl` 文件
- 重新运行脚本并登录

### 4. 评论失败?

**可能原因**:
- 网络问题
- 页面加载超时
- 风控限制
- 评论框选择器变化

**解决方法**:
- 检查网络连接
- 增加 `MIN_INTERVAL` 间隔时间
- 查看日志文件了解详细错误信息

### 5. 重复评论同一篇笔记?

**可能原因**:
- 数据库文件损坏或被删除

**解决方法**:
- 检查 `xhs_commented_notes.db` 文件是否存在
- 不要手动删除数据库文件

---

## 📝 更新日志

### V5.1 (2025-10-27)

**新增功能**:
- ✨ 图形化配置面板 (`config_gui.py`)
- ✨ 实时风险等级提示
- ✨ 可视化评论库管理
- ✨ 一键启动配置面板脚本

**优化改进**:
- 🔧 降低使用门槛,适合小白用户
- 🔧 无需手动编辑配置文件
- 🔧 配置错误验证和提示

### V5.0 (2025-01-15)

**新增功能**:
- ✨ 启动时自动清理 Chrome 进程
- ✨ SQLite 数据库记录已评论笔记
- ✨ 自动日志导出功能
- ✨ 配置文件分离 (`config.py`)

**优化改进**:
- 🔧 增强登录状态检测
- 🔧 优化弹出层关闭逻辑
- 🔧 改进异常处理机制
- 🔧 完善运行统计报告

**Bug 修复**:
- 🐛 修复进程冲突导致的启动失败
- 🐛 修复重复评论同一篇笔记的问题
- 🐛 修复日志记录不完整的问题

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

## 📧 联系方式

如有问题或建议,请通过以下方式联系:

- GitHub Issues: [提交问题](https://github.com/peter-pan-x/XHS-AUTOCOMMENT/issues)
- Email: [您的邮箱]

---

## ⭐ Star History

如果这个项目对您有帮助,请给我们一个 Star ⭐️

---

<div align="center">

**Made with ❤️ by peter-pan-x**

</div>


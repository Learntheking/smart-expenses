# Smart Expenses 📊

**自然语言记账 — 一个 Claude Code 技能**

用日常说话的方式记账。无需打开 App、无需手动选分类、无需填表格。在终端里跟 Claude 说"中午外卖35块"，它就帮你记好了。月底一键生成消费报告。

## ✨ 功能亮点

- **自然语言输入** — "昨天打车18"、"超市买菜花了120"、"交房租2500"，像聊天一样记账
- **智能分类** — 自动根据描述推断消费类别（餐饮、交通、购物等10大类）
- **灵活日期** — 支持"今天"、"昨天"、"前天"、"上周五"等自然语言日期
- **可视化报告** — 月度消费报告，ASCII 图表展示分类占比和每日趋势
- **多维查询** — 按关键词搜索、列出最近记录、快速概览、数据导出
- **隐私优先** — 数据存储在本地 `~/.smart-expenses/expenses.csv`，纯文本，完全由你掌控
- **可自定义** — 自由添加/删除消费分类，支持人民币/美元切换

## 📸 效果预览

### 记账
```
用户: 中午外卖35块

Claude: ✓ 已记录 #12: 外卖午餐 | ¥35.00 | 餐饮饮食 | 2026-06-09
```

### 查看消费概览
```
用户: /smart-expenses summary

Claude:
💰 本月已消费: ¥3,240.50 (23 笔)
   较上月: -¥520.00
📊 本月消费 TOP3:
   餐饮饮食: ¥1,250.00
   交通出行: ¥680.50
   购物消费: ¥520.00
📈 日均消费: ¥108.02 | 预估全月: ¥3,240.50
```

### 月度报告
```
用户: /smart-expenses report

输出带 ASCII 图表的完整月度消费报告，包含:
- 总支出 & 笔数 & 日均
- 分类占比条形图
- 每日消费趋势图
```

## 📦 安装

### 前置条件

- [Claude Code](https://code.claude.com) 已安装
- Python 3.7+（仅使用标准库，无需安装额外依赖）

### 方式一：个人安装（推荐，所有项目可用）

```bash
# 1. 克隆仓库
git clone https://github.com/Learntheking/smart-expenses.git

# 2. 安装技能到 Claude Code 个人目录
mkdir -p ~/.claude/skills/smart-expenses
cp -r smart-expenses/* ~/.claude/skills/smart-expenses/
```

### 方式二：项目级安装

```bash
# 在项目根目录下
mkdir -p .claude/skills/smart-expenses
cp -r /path/to/smart-expenses/* .claude/skills/smart-expenses/
```

### 方式三：直接复制（最简单）

```bash
# 克隆后直接复制 SKILL.md 和脚本
git clone https://github.com/Learntheking/smart-expenses.git
cp -r smart-expenses ~/.claude/skills/
```

## 🚀 快速开始

安装后无需任何配置，直接在 Claude Code 中开始使用：

```bash
# 启动 Claude Code
claude

# 开始记账（自然语言）
中午外卖35块
昨天打车18
超市买菜花了120.5

# 查看最近记录
/smart-expenses list

# 查看本月概览
/smart-expenses summary

# 生成月度报告
/smart-expenses report

# 搜索记录
/smart-expenses search 外卖

# 导出数据
/smart-expenses export
```

## 📂 数据存储

所有记账数据存储在：

```
~/.smart-expenses/
├── expenses.csv      # 消费记录（CSV 格式）
└── config.json       # 配置文件（分类、货币等）
```

CSV 文件结构：
| id | date | amount | category | description | notes |
|----|------|--------|----------|-------------|-------|
| 1 | 2026-06-09 | 35.0 | 餐饮饮食 | 外卖午餐 | |

你可以用 Excel、Numbers、或任何文本编辑器打开查看和编辑。

## 🎯 使用技巧

### 带日期记账
```
用户: 上周五看电影68元
Claude: ✓ 已记录: 看电影 | ¥68.00 | 休闲娱乐 | 2026-06-05
```

### 连续记账
```
用户: 今天记几笔：早餐15，午餐外卖40，晚上打车回家35
Claude: (依次记录三笔，并给出鼓励)
```

### 添加自定义分类
```
用户: 添加一个"宠物"分类
/smart-expenses categories --add 宠物用品
```

### 删除错误记录
```
用户: 删掉第5条
/smart-expenses delete 5
```

## 🔧 技能架构

```
smart-expenses/
├── SKILL.md              # 技能主文件 — Claude 的行为指令
├── README.md             # 项目说明（本文件）
├── REFERENCE.md          # 详细参考文档
└── scripts/
    └── expense.py        # Python 核心引擎（CRUD + 报告 + 导出）
```

**工作原理：**
1. SKILL.md 描述技能用途和触发条件，Claude 自动加载
2. 用户输入自然语言 → Claude 解析金额/分类/日期/描述
3. Claude 调用 `expense.py` 执行数据操作
4. `expense.py` 读写本地 CSV/JSON 文件
5. Claude 将结果友好地呈现给用户

## 📄 开源协议

MIT License — 自由使用、修改、分发。

## 🤝 贡献

欢迎提 Issue 和 PR！如果你有好的想法，比如：
- 预算管理功能
- 更多图表类型
- 多币种支持
- 账单导入功能
- i18n 国际化

请随时参与贡献。

---

**Made with ❤️ for the open-source community**

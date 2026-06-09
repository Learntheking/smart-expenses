---
name: Smart Expenses
description: Natural language expense tracking. Use when the user wants to log expenses, record spending, track money, check budgets, generate expense reports, or manage personal finances. Trigger phrases include "记账", "花了", "消费", "支出", "花销", "记录了", "买了", "账单", "花了多少钱", "我这个月花了多少".
argument-hint: [记账内容 | report | list | summary]
allowed-tools: Bash(python3 *) Read
---

# Smart Expenses — 自然语言记账

## 脚本位置
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py <command> [args]
```

## 核心工作流程

### 1. 解析自然语言记账

当用户输入自然语言描述一笔消费时（例如 "中午外卖35块"、"打车18元"），你需要：

1. **提取金额** — 识别数字 + 货币单位（块/元/¥/$/刀）
2. **判断分类** — 根据描述推断最合适的分类（见下方分类参考）
3. **提取描述** — 去掉金额部分，保留简洁的描述文字
4. **推断日期** — 默认为今天，如果用户说"昨天"/"前天"/"上周五"等则相应调整
5. **提取备注** — 如果有额外的上下文信息

**解析示例：**

| 用户输入 | 金额 | 分类 | 描述 | 日期 |
|---------|------|------|------|------|
| 中午外卖35块 | 35 | 餐饮饮食 | 外卖午餐 | 今天 |
| 昨天打车18 | 18 | 交通出行 | 打车 | 昨天 |
| 买了件卫衣299 | 299 | 购物消费 | 卫衣 | 今天 |
| 交房租2500 | 2500 | 住房房租 | 房租 | 今天 |
| 上周五看电影68 | 68 | 休闲娱乐 | 看电影 | 上周五 |
| 挂号费50 | 50 | 医疗健康 | 挂号费 | 今天 |
| 充话费100 | 100 | 通讯网络 | 充话费 | 今天 |
| 超市买菜花了120.5 | 120.5 | 日常用品 | 超市买菜 | 今天 |
| 买书两本89元 | 89 | 教育学习 | 买书两本 | 今天 |

### 2. 调用脚本执行操作

解析完成后，调用脚本记录：

```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py add --amount <金额> --category <分类> --desc "<描述>" --date <YYYY-MM-DD> [--notes "<备注>"]
```

然后友好地回复用户，确认已记录。格式：已记录：<描述> | ¥<金额> | <分类> | <日期>

### 3. 其他命令

**查看最近记录:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py list [数量，默认20]
```

**生成月报:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py report [YYYY-MM，默认当月]
```

**快速概览:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py summary
```

**删除记录:**
先询问用户确认，然后：
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py delete <id>
```

**搜索记录:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py search <关键词>
```

**管理分类:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py categories                     # 查看所有分类
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py categories --add "<新分类>"     # 添加分类
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py categories --remove "<分类>"   # 删除分类
```

**导出数据:**
```
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py export                  # 导出为 JSON
python3 ${CLAUDE_SKILL_DIR}/scripts/expense.py export --format csv     # 导出为 CSV
```

## 分类参考

默认分类及关键词匹配规则：

| 分类 | 关键词 |
|------|--------|
| 餐饮饮食 | 外卖、饭、菜、餐厅、食堂、奶茶、咖啡、饮料、早餐、午餐、晚餐、烧烤、火锅、零食、水果、聚餐、请客 |
| 交通出行 | 打车、滴滴、地铁、公交、高铁、机票、加油、停车、共享单车、出租车、网约车 |
| 购物消费 | 买了、衣服、鞋子、包包、电子产品、数码、淘宝、京东、网购、商场、超市 |
| 住房房租 | 房租、房贷、物业、水电、燃气、网费、维修 |
| 休闲娱乐 | 电影、KTV、游戏、旅游、景点、门票、演唱会、聚会、酒吧、剧本杀、健身、运动 |
| 医疗健康 | 挂号、药、医院、体检、牙科、门诊、保险 |
| 教育学习 | 书、课程、培训、考试、报名、学费、文具 |
| 通讯网络 | 话费、流量、网费、宽带、VPN |
| 日常用品 | 日用品、洗漱、纸巾、洗发水、买菜、超市 |
| 其他支出 | 无法归类到以上分类的支出 |

## 重要提醒

- **始终用友好、鼓励的语气回复**，记账是件需要坚持的事，适当的正向反馈很重要
- 数据存储在 `~/.smart-expenses/expenses.csv`，纯文本格式，用户完全掌控自己的数据
- 如果用户连续记账多笔，在第三笔后可以给个小鼓励（如 "今天已经记了3笔，坚持得很棒！💪"）
- 生成报告时，如果发现超支趋势，给出温和的提醒和建议
- 支持人民币(¥)和美元($)，默认人民币。可通过配置文件切换
- 用户说"花了..."、"消费..."、"用了..."、"付了..."、"买了..."时，自动识别为记账意图

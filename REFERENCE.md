# Smart Expenses — 参考文档

## 数据文件格式

### expenses.csv

```csv
id,date,amount,category,description,notes
1,2026-06-09,35.0,餐饮饮食,外卖午餐,
2,2026-06-08,18.0,交通出行,打车,下雨打车回家
```

### config.json

```json
{
  "categories": [
    "餐饮饮食",
    "交通出行",
    "购物消费",
    "住房房租",
    "休闲娱乐",
    "医疗健康",
    "教育学习",
    "通讯网络",
    "日常用品",
    "其他支出"
  ],
  "currency": "CNY",
  "created_at": "2026-06-09"
}
```

## Python 脚本命令参考

### add — 添加消费记录
```
python3 expense.py add --amount <数字> --category <分类> --desc "<描述>" [--date YYYY-MM-DD] [--notes "<备注>"]
```

### list — 列出最近记录
```
python3 expense.py list [数量, 默认20]
```

### report — 生成月度报告
```
python3 expense.py report [YYYY-MM, 默认当月]
```
报告包含：
- 总支出和笔数
- 日均消费
- 分类占比条形图（ASCII █）
- 每日消费趋势

### delete — 删除记录
```
python3 expense.py delete <id>
```

### categories — 管理分类
```
python3 expense.py categories                     # 查看
python3 expense.py categories --add "<名称>"       # 添加
python3 expense.py categories --remove "<名称>"    # 删除
```

### export — 导出数据
```
python3 expense.py export                  # JSON 格式
python3 expense.py export --format csv     # CSV 格式
```

### summary — 快速概览
```
python3 expense.py summary
```
显示：本月消费总额、较上月变化、TOP3 分类、日均和预估

### search — 关键词搜索
```
python3 expense.py search <关键词>
```

## 分类自动匹配规则

Claude 根据用户描述中的关键词自动推断分类：

| 分类 | 典型关键词 |
|------|-----------|
| 餐饮饮食 | 外卖、吃饭、餐厅、食堂、奶茶、咖啡、饮料、早餐、午餐、晚餐、烧烤、火锅、零食、水果、聚餐、请客、买菜（菜市场） |
| 交通出行 | 打车、滴滴、地铁、公交、高铁、机票、火车票、加油、停车费、共享单车、出租车、网约车、顺风车 |
| 购物消费 | 买（衣服/鞋/包/电子）、淘宝、京东、拼多多、网购、商场、衣服、鞋子、包包、数码、电器、化妆品 |
| 住房房租 | 房租、房贷、物业费、水电费、燃气费、取暖费、维修、装修 |
| 休闲娱乐 | 电影、KTV、唱歌、游戏、旅游、景点、门票、演唱会、酒吧、剧本杀、密室、健身、游泳、按摩 |
| 医疗健康 | 挂号、看病、药、医院、体检、牙科、门诊、急诊、住院、检查费 |
| 教育学习 | 书、课程、培训、考试、报名费、学费、文具、网课、电子书 |
| 通讯网络 | 话费、流量、宽带、网费、VPN、电话费 |
| 日常用品 | 日用品、洗漱、纸巾、洗发水、沐浴露、洗衣液、超市（非食品）、买菜（超市） |
| 其他支出 | 转账、红包、捐款、快递费、罚款、无法归类 |

## 货币支持

默认货币为人民币（CNY），符号 ¥。如需切换为美元：

编辑 `~/.smart-expenses/config.json`：
```json
{
  "currency": "USD"
}
```

## Claude Code 技能配置参考

技能的完整配置在 `SKILL.md` 的 YAML 前导部分：

```yaml
name: Smart Expenses
description: ...
argument-hint: [记账内容 | report | list | summary]
allowed-tools: Bash(python3 *) Read
```

- `name` — 技能显示名称
- `description` — Claude 据此决定何时自动调用技能
- `argument-hint` — 用户输入 `/smart-expenses` 时的提示
- `allowed-tools` — 技能运行时免审批的工具

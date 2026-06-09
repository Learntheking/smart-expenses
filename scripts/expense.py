#!/usr/bin/env python3
"""
Smart Expenses — Natural language expense tracking engine.

Usage:
  python expense.py add --amount 35 --category 餐饮 --desc "外卖" [--date 2026-06-09] [--notes "..."]
  python expense.py list [count]
  python expense.py report [YYYY-MM]
  python expense.py delete <id>
  python expense.py categories [--add <name> --remove <name>]
  python expense.py export [--format json|csv]
  python expense.py summary
  python expense.py search <keyword>
"""

import csv
import io
import json
import os
import sys
import shutil

# Fix Unicode output on Windows GBK consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import datetime, date, timedelta
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path.home() / ".smart-expenses"
DATA_FILE = DATA_DIR / "expenses.csv"
CONFIG_FILE = DATA_DIR / "config.json"

DEFAULT_CATEGORIES = [
    "餐饮饮食",  # Food & Dining
    "交通出行",  # Transportation
    "购物消费",  # Shopping
    "住房房租",  # Housing & Rent
    "休闲娱乐",  # Entertainment
    "医疗健康",  # Healthcare
    "教育学习",  # Education
    "通讯网络",  # Communication
    "日常用品",  # Daily Supplies
    "其他支出",  # Others
]

COLUMNS = ["id", "date", "amount", "category", "description", "notes"]

BAR_WIDTH = 40


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("id,date,amount,category,description,notes\n", encoding="utf-8")
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({
            "categories": DEFAULT_CATEGORIES,
            "currency": "CNY",
            "created_at": date.today().isoformat()
        }, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def read_expenses():
    if not DATA_FILE.exists():
        return []
    rows = []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["amount"] = float(r["amount"])
            r["id"] = int(r["id"])
            rows.append(r)
    return rows


def write_expenses(rows):
    with DATA_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in COLUMNS})


def next_id(rows):
    return max([r["id"] for r in rows], default=0) + 1


def cmd_add(args):
    ensure_data_dir()
    rows = read_expenses()

    amount = None
    category = None
    desc = None
    expense_date = date.today().isoformat()
    notes = ""

    i = 0
    while i < len(args):
        if args[i] == "--amount" and i + 1 < len(args):
            amount = float(args[i + 1]); i += 2
        elif args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1]; i += 2
        elif args[i] == "--desc" and i + 1 < len(args):
            desc = args[i + 1]; i += 2
        elif args[i] == "--date" and i + 1 < len(args):
            expense_date = args[i + 1]; i += 2
        elif args[i] == "--notes" and i + 1 < len(args):
            notes = args[i + 1]; i += 2
        else:
            i += 1

    if amount is None or category is None or desc is None:
        print("Error: --amount, --category, and --desc are required")
        sys.exit(1)

    new_row = {
        "id": next_id(rows),
        "date": expense_date,
        "amount": amount,
        "category": category,
        "description": desc,
        "notes": notes,
    }
    rows.append(new_row)
    write_expenses(rows)

    print(f"✓ 已记录 #{new_row['id']}: {new_row['description']} | ¥{new_row['amount']:.2f} | {new_row['category']} | {new_row['date']}")


def cmd_list(args):
    ensure_data_dir()
    rows = read_expenses()
    count = int(args[0]) if args and args[0].isdigit() else 20
    recent = rows[-count:]

    if not recent:
        print("暂无消费记录，用 `/smart-expenses <描述>` 来添加第一条吧！")
        return

    print(f"{'ID':<5} {'日期':<12} {'金额':<10} {'分类':<10} {'描述'}")
    print("-" * 60)
    for r in reversed(recent):
        day_of_week = datetime.strptime(r["date"], "%Y-%m-%d").strftime("%a")
        print(f"#{r['id']:<4} {r['date']} {day_of_week}  ¥{r['amount']:<8.2f} {r['category']:<10} {r['description']}")


def cmd_report(args):
    ensure_data_dir()
    rows = read_expenses()
    today = date.today()

    if args:
        target = args[0]
    else:
        target = today.strftime("%Y-%m")

    config = load_config()
    currency = config.get("currency", "CNY")
    symbol = "¥" if currency == "CNY" else "$"

    if len(target) == 7:  # YYYY-MM
        filtered = [r for r in rows if r["date"].startswith(target)]
        year, month = int(target[:4]), int(target[5:7])
        period_label = f"{year}年{month}月"
    else:
        filtered = [r for r in rows if r["date"].startswith(target)]
        period_label = target

    if not filtered:
        print(f"📊 {period_label} 暂无消费记录")
        return

    total = sum(r["amount"] for r in filtered)
    by_category = defaultdict(float)
    for r in filtered:
        by_category[r["category"]] += r["amount"]

    sorted_cats = sorted(by_category.items(), key=lambda x: -x[1])
    max_amount = sorted_cats[0][1] if sorted_cats else 1

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  📊 {period_label} 消费报告{' ' * (28 - len(period_label))}║")
    print(f"╠══════════════════════════════════════════════════╣")
    print(f"║  总支出: {symbol}{total:>10.2f}                         ║")
    print(f"║  笔数:   {len(filtered):>10}                           ║")
    print(f"║  日均:   {symbol}{total / max(datetime(year, month, 1).day, today.day):>10.2f}                         ║")
    print(f"╠══════════════════════════════════════════════════╣")

    for cat, amt in sorted_cats:
        bar_len = int(amt / max_amount * BAR_WIDTH)
        bar = "█" * bar_len + "░" * (BAR_WIDTH - bar_len)
        pct = amt / total * 100
        print(f"║  {cat:<8} {bar} ║")
        print(f"║           {symbol}{amt:>8.2f} ({pct:>5.1f}%){' ' * 18}║")

    print(f"╚══════════════════════════════════════════════════╝")

    # Trend: daily spending line chart (ASCII)
    daily = defaultdict(float)
    for r in filtered:
        daily[r["date"]] += r["amount"]
    if len(daily) > 1:
        dates = sorted(daily.keys())
        print(f"\n📈 每日消费趋势")
        amounts = [daily[d] for d in dates]
        max_daily = max(amounts)
        for d in dates:
            bar_len = int(daily[d] / max_daily * 30) if max_daily > 0 else 0
            bar = "█" * bar_len
            print(f"  {d[-5:]} {bar} {symbol}{daily[d]:.0f}")


def cmd_delete(args):
    ensure_data_dir()
    if not args:
        print("Usage: python expense.py delete <id>")
        sys.exit(1)
    target_id = int(args[0])
    rows = read_expenses()
    target = next((r for r in rows if r["id"] == target_id), None)
    if target is None:
        print(f"未找到 #{target_id}")
        sys.exit(1)
    rows = [r for r in rows if r["id"] != target_id]
    write_expenses(rows)
    print(f"✓ 已删除 #{target_id}: {target['description']} | ¥{target['amount']:.2f}")


def cmd_categories(args):
    ensure_data_dir()
    config = load_config()
    cats = config.get("categories", DEFAULT_CATEGORIES)

    if not args:
        print("当前分类:")
        for i, c in enumerate(cats, 1):
            print(f"  {i}. {c}")
        return

    if "--add" in args:
        idx = args.index("--add")
        if idx + 1 < len(args):
            new_cat = args[idx + 1]
            if new_cat not in cats:
                cats.append(new_cat)
                config["categories"] = cats
                save_config(config)
                print(f"✓ 已添加分类: {new_cat}")

    if "--remove" in args:
        idx = args.index("--remove")
        if idx + 1 < len(args):
            rm_cat = args[idx + 1]
            if rm_cat in cats:
                cats.remove(rm_cat)
                config["categories"] = cats
                save_config(config)
                print(f"✓ 已删除分类: {rm_cat}")


def cmd_export(args):
    ensure_data_dir()
    rows = read_expenses()
    fmt = "json"
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            fmt = args[idx + 1]

    if fmt == "csv":
        shutil.copy(DATA_FILE, "expenses_export.csv")
        print("✓ 已导出到 expenses_export.csv")
    else:
        export_path = "expenses_export.json"
        Path(export_path).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 已导出 {len(rows)} 条记录到 {export_path}")


def cmd_summary(args=None):
    ensure_data_dir()
    rows = read_expenses()
    if not rows:
        print("暂无消费记录")
        return

    today = date.today()
    this_month = today.strftime("%Y-%m")
    last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    this_month_rows = [r for r in rows if r["date"].startswith(this_month)]
    last_month_rows = [r for r in rows if r["date"].startswith(last_month)]

    this_total = sum(r["amount"] for r in this_month_rows)
    last_total = sum(r["amount"] for r in last_month_rows)

    print(f"💰 本月已消费: ¥{this_total:.2f} ({len(this_month_rows)} 笔)")
    if last_total > 0:
        delta = this_total - last_total
        sign = "+" if delta > 0 else ""
        print(f"   较上月: {sign}¥{delta:.2f}")

    # Top categories this month
    if this_month_rows:
        by_cat = defaultdict(float)
        for r in this_month_rows:
            by_cat[r["category"]] += r["amount"]
        top = sorted(by_cat.items(), key=lambda x: -x[1])[:3]
        print(f"📊 本月消费 TOP3:")
        for cat, amt in top:
            print(f"   {cat}: ¥{amt:.2f}")

    # Day of current month
    day_count = today.day
    avg_daily = this_total / day_count if day_count > 0 else 0
    month_projection = avg_daily * 30
    print(f"📈 日均消费: ¥{avg_daily:.2f} | 预估全月: ¥{month_projection:.2f}")


def cmd_search(args):
    ensure_data_dir()
    if not args:
        print("Usage: python expense.py search <keyword>")
        sys.exit(1)
    keyword = args[0].lower()
    rows = read_expenses()
    matches = [r for r in rows if keyword in r["description"].lower() or keyword in r["category"].lower() or keyword in r.get("notes", "").lower()]
    if not matches:
        print(f"未找到包含 '{keyword}' 的记录")
        return
    print(f"🔍 找到 {len(matches)} 条包含 '{keyword}' 的记录:")
    print(f"{'ID':<5} {'日期':<12} {'金额':<10} {'分类':<10} {'描述'}")
    print("-" * 60)
    for r in reversed(matches):
        print(f"#{r['id']:<4} {r['date']}  ¥{r['amount']:<8.2f} {r['category']:<10} {r['description']}")


# ── Natural language parsing (standalone mode, no Claude needed) ──────────────

CATEGORY_KEYWORDS = [
    ("住房房租", "房租|房贷|物业|水电费|燃气|取暖|维修"),
    ("交通出行", "打车|滴滴|地铁|公交|高铁|火车票|机票|加油|停车|共享单车|出租车|网约车|顺风车|骑行|地铁卡"),
    ("日常用品", "日用品|洗漱|纸巾|洗发水|沐浴露|洗衣液|买菜|超市|牙膏|毛巾|垃圾袋|洗衣|清洁"),
    ("餐饮饮食", "外卖|餐厅|食堂|奶茶|咖啡|饮料|早餐|午餐|晚餐|晚饭|早饭|午饭|烧烤|火锅|零食|水果|聚餐|请客|包子|饺子|面条|汉堡|披萨|炸鸡|面包"),
    ("购物消费", "买了|衣服|鞋子|包包|电子|数码|淘宝|京东|网购|商场|化妆品|护肤品|卫衣|裤子|裙子|帽子|袜子|手机|电脑|耳机|家电|家具"),
    ("休闲娱乐", "电影|KTV|唱歌|游戏|旅游|景点|门票|演唱会|酒吧|剧本杀|密室|健身|游泳|按摩|聚会|ktv|游乐"),
    ("医疗健康", "挂号|看病|药|医院|体检|牙科|门诊|急诊|住院|检查|买药|诊所"),
    ("教育学习", "书|课程|培训|考试|报名|学费|文具|网课|电子书|买书|教材"),
    ("通讯网络", "话费|流量|宽带|网费|VPN|电话费|充话费|充值"),
]

DATE_PATTERNS = [
    (r"今天", 0),
    (r"昨天", 1),
    (r"前天", 2),
    (r"大前天", 3),
    (r"上周一", lambda: _day_offset_last_week(0)),
    (r"上周二", lambda: _day_offset_last_week(1)),
    (r"上周三", lambda: _day_offset_last_week(2)),
    (r"上周四", lambda: _day_offset_last_week(3)),
    (r"上周五", lambda: _day_offset_last_week(4)),
    (r"上周六", lambda: _day_offset_last_week(5)),
    (r"上周日|上周末", lambda: _day_offset_last_week(6)),
    (r"前天", 2),
    (r"(\d+)天前", lambda m: int(m.group(1))),
]

def _day_offset_last_week(weekday):
    """Days from today to the given weekday last week."""
    today = date.today()
    days_since = today.weekday() - weekday
    if days_since < 0:
        days_since += 7
    return days_since + 7

def parse_date(text):
    """Extract date from natural language text. Returns (date_iso, cleaned_text)."""
    import re
    today = date.today()

    for pattern, offset in DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            if callable(offset):
                days = offset(m) if m.groups() else offset()
            else:
                days = offset
            result_date = today - timedelta(days=days)
            text = re.sub(pattern, "", text).strip()
            return result_date.isoformat(), text

    # Check for explicit YYYY-MM-DD or MM-DD
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        text = text.replace(m.group(1), "").strip()
        return m.group(1), text
    m = re.search(r"(\d{1,2})月(\d{1,2})[号日]", text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        text = re.sub(r"\d{1,2}月\d{1,2}[号日]", "", text).strip()
        return f"{today.year}-{month:02d}-{day:02d}", text

    return today.isoformat(), text

def parse_amount(text):
    """Extract monetary amount from natural language text. Returns (amount, cleaned_text)."""
    import re
    # ¥123.45, 123.45元, 123块, 123.5块, $50
    m = re.search(r"[¥$]?\s*(\d+(?:\.\d{1,2})?)\s*(?:元|块|刀|美元|美金)?", text)
    if m:
        amount = float(m.group(1))
        text = re.sub(r"[¥$]?\s*\d+(?:\.\d{1,2})?\s*(?:元|块|刀|美元|美金)?", "", text, count=1).strip()
        return amount, text
    return None, text

def parse_category(text):
    """Infer expense category from description text."""
    import re
    for cat, pattern in CATEGORY_KEYWORDS:
        if re.search(pattern, text):
            return cat
    return "其他支出"

def cmd_nl(args):
    """Natural language expense entry: python expense.py 中午外卖35块"""
    ensure_data_dir()
    import re

    raw = " ".join(args).strip()
    if not raw:
        print("Usage: python expense.py <自然语言描述>")
        print('Example: python expense.py 中午外卖35块')
        sys.exit(1)

    text = raw

    # Extract date
    expense_date, text = parse_date(text)

    # Extract amount
    amount, text = parse_amount(text)
    if amount is None:
        print(f"❌ 未能识别金额，请在描述中包含数字金额（如 35块、100元）")
        print(f"   输入: {raw}")
        sys.exit(1)

    # Infer category
    category = parse_category(text)

    # Clean description
    import re
    desc = text.strip()
    # Remove filler words
    desc = re.sub(r"(花了|用了|买了|交了|付了|消费|花了|买了)", "", desc)
    # Remove leading measure words
    desc = re.sub(r"^[个件双支本张台辆杯碗盘份次趟]", "", desc)
    desc = desc.strip().lstrip("，,。的 ").strip()
    if not desc:
        desc = re.sub(r"[¥$]?\s*\d+(?:\.\d+)?\s*(?:元|块|刀|美元|美金)?", "", raw).strip()
        desc = re.sub(r"(花了|用了|买了|交了|付了)", "", desc).strip()
    if len(desc) > 30:
        desc = desc[:30]

    # Save
    rows = read_expenses()
    new_row = {
        "id": next_id(rows),
        "date": expense_date,
        "amount": round(amount, 2),
        "category": category,
        "description": desc,
        "notes": "",
    }
    rows.append(new_row)
    write_expenses(rows)

    print(f"✓ #{new_row['id']} | {new_row['description']} | ¥{new_row['amount']:.2f} | {new_row['category']} | {new_row['date']}")


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "report": cmd_report,
    "delete": cmd_delete,
    "categories": cmd_categories,
    "export": cmd_export,
    "summary": cmd_summary,
    "search": cmd_search,
    "nl": cmd_nl,
}


def main():
    if len(sys.argv) < 2:
        print("Smart Expenses — Natural language expense tracking")
        print(f"Data: {DATA_FILE}")
        print()
        print("Commands: add | list | report | delete | categories | export | summary | search | nl")
        print()
        print("Quick examples (standalone, no Claude needed):")
        print('  python expense.py 中午外卖35块')
        print('  python expense.py 昨天打车18元')
        print('  python expense.py list 10')
        print("  python expense.py report")
        print("  python expense.py summary")
        return

    # If first arg isn't a known command, treat as natural language
    if sys.argv[1] in COMMANDS:
        COMMANDS[sys.argv[1]](sys.argv[2:])
    else:
        cmd_nl(sys.argv[1:])


if __name__ == "__main__":
    main()

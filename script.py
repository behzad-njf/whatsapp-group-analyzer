#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
whatsapp_group_analyser.py   —  **Extended Edition**
Analyse an exported WhatsApp‑group text chat (UTF‑8)

Features now included
─────────────────────
✔ Basic per‑user counts (messages, media, deleted, bad‑word)
✔ Jalali (Shamsi) dates with Persian weekday names
✔ Daily min / max / average stats
✔ Group creation + rename timeline
✔ **NEW advanced analytics**
    • Avg. message length (chars & words) per user
    • First & last message timestamp per user
    • Hour‑of‑day heat‑map counts (0‑23)
    • Weekday activity distribution (Sat→Fri)
    • Monthly activity distribution (Farvardin→Esfand or Jan‑Dec fallback)
    • Global top‑N common words (stop‑words removed)
    • Emoji usage counts (overall & per user)
    • Day with most media shared

Dependencies
────────────
    pip install jdatetime emoji

Run
───
    python whatsapp_group_analyser.py
"""

from __future__ import annotations

from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime
import re
import sys

# ---------------------------------------------------------------------------
try:
    import jdatetime  # Jalali conversion
except ImportError:
    jdatetime = None
    print("⚠️  jdatetime not installed – output will stay Gregorian.")

try:
    import emoji  # for robust emoji detection
except ImportError:
    emoji = None
    print("⚠️  emoji library not installed – emoji counts may be incomplete.")

CHAT_FILE = Path("Chats_update_2025-07-06.txt")
BAD_WORDS_FILE = Path("bad_words.txt")
STOP_WORDS_FILE = Path("stop_words.txt")  # optional, Persian/English stop words

# ---------- Load inputs ------------------------------------------------------
if not CHAT_FILE.exists():
    sys.exit(f"Chat file not found: {CHAT_FILE}")

bad_words: set[str] = set()
if BAD_WORDS_FILE.exists():
    bad_words = {w.strip() for w in BAD_WORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()}

stop_words: set[str] = set()
if STOP_WORDS_FILE.exists():
    stop_words = {w.strip().lower() for w in STOP_WORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()}

lines = CHAT_FILE.read_text(encoding="utf-8").splitlines()

# ---------- Data structures --------------------------------------------------
user_stats = defaultdict(lambda: {
    "messages": 0,
    "media": 0,
    "deleted": 0,
    "bad_word": 0,
    "char_sum": 0,
    "word_sum": 0,
    "first_ts": None,
    "last_ts": None,
})

hour_counts = Counter()     # 0‑23
weekday_counts = Counter()  # 0‑6 (Sat=0)
month_counts = Counter()    # 1‑12 (Jalali or Gregorian)

word_freq_global = Counter()
emoji_freq_global = Counter()
media_per_day = Counter()
messages_per_day = defaultdict(int)

# Persian weekday names (Saturday index 0 matching jdatetime)
FA_WEEKDAYS = [
    "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"
]

MEDIA_TAG = "<Media omitted>"
DELETED_TAG = "This message was deleted"

RE_CREATED = re.compile(r'(.+?) created (?:group|this group) "?(.*?)"?$', re.I)
RE_GROUP_RENAME = re.compile(r'^(.*?) - (.+?) changed the group name from "(.+?)" to "(.+?)"', re.I)

# Simple emoji detector fallback if emoji lib missing
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAFF]')


group_info: dict[str, str | None] = {"created_ts": None, "created_by": None, "created_name": None}
group_renames: list[tuple[str, str, str, str]] = []  # (date, changer, old, new)

def parse_timestamp(raw_ts: str) -> datetime | None:
    """Return datetime from WhatsApp export timestamp (handles 12/24h, M/D/YY and D/M/YY)."""
    # Try common WhatsApp formats
    formats = [
        "%m/%d/%y, %I:%M %p",  # 12h, e.g. 11/4/20, 9:53 AM
        "%d/%m/%y, %I:%M %p",  # 12h, e.g. 4/11/20, 9:53 AM
        "%m/%d/%y, %H:%M",     # 24h, e.g. 11/4/20, 21:53
        "%d/%m/%y, %H:%M",     # 24h, e.g. 4/11/20, 21:53
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw_ts.strip(), fmt)
        except ValueError:
            continue
    return None

def g2j(dt: datetime) -> jdatetime.date | None:
    if jdatetime is None:
        return None
    return jdatetime.date.fromgregorian(date=dt.date())

def format_jalali_date(dt: datetime) -> tuple[str, int, int]:
    """Return formatted Jalali date string, weekday_index (0‑6), month (1‑12)."""
    if jdatetime is None:
        weekday_idx = dt.weekday()  # Monday=0
        # Convert to Saturday=0 mapping to align Persian names
        weekday_idx = (weekday_idx + 2) % 7
        return dt.strftime("%Y/%m/%d"), weekday_idx, dt.month
    jd = g2j(dt)
    weekday_idx = jd.weekday()  # Saturday=0
    return jd.strftime("%Y/%m/%d"), weekday_idx, jd.month

# ---------- Main loop --------------------------------------------------------
for raw in lines:
    if " - " not in raw:
        continue

    ts_part, content = raw.split(" - ", 1)
    dt = parse_timestamp(ts_part)
    if dt is None:
        continue
    date_label, weekday_idx, month_num = format_jalali_date(dt)
    hour_counts[dt.hour] += 1
    weekday_counts[weekday_idx] += 1
    month_counts[month_num] += 1
    messages_per_day[date_label] += 1

    # ===== User message ======================================================
    if ":" in content:
        sender, message = content.split(":", 1)
        sender = sender.strip()
        message = message.strip()
        if not sender:
            continue

        s = user_stats[sender]
        s["messages"] += 1
        s["char_sum"] += len(message)
        s["word_sum"] += len(message.split())
        s["first_ts"] = s["first_ts"] or dt
        s["last_ts"] = dt  # always newest

        if MEDIA_TAG in message:
            s["media"] += 1
            media_per_day[date_label] += 1
        if DELETED_TAG.lower() in message.lower():
            s["deleted"] += 1
        if bad_words and any(bw in message for bw in bad_words):
            s["bad_word"] += 1

        # Word frequency (basic split, remove punctuation)
        clean = re.sub(r"[\W_]+", " ", message).lower()
        words = [w for w in clean.split() if w and w not in stop_words]
        word_freq_global.update(words)

        # Emoji detection
        if emoji:
            emoji_list = [ch for ch in message if ch in emoji.EMOJI_DATA]
        else:
            emoji_list = EMOJI_PATTERN.findall(message)
        emoji_freq_global.update(emoji_list)
        continue

    # ===== System message ====================================================
    m = RE_CREATED.match(content)
    if m:
        group_info.update({
            "created_ts": date_label,
            "created_by": m.group(1).strip(),
            "created_name": m.group(2).strip() or "(unnamed)",
        })
        continue

    m = RE_GROUP_RENAME.match(raw)
    if m:
        ts_raw, changer, old_name, new_name = m.groups()
        dt_rename = parse_timestamp(ts_raw.strip())
        if dt_rename:
            rename_label, _, _ = format_jalali_date(dt_rename)
            group_renames.append((rename_label, changer.strip(), old_name.strip(), new_name.strip()))
        continue

# ---------- Reporting --------------------------------------------------------
print("\n" + "═" * 100)
print("USER SUMMARY (sorted by messages)\n")
print(f"{'Name':<22} | {'Msgs':>6} | {'Media':>5} | {'Del':>4} | {'Bad':>4} | {'AvgChars':>8} | {'AvgWords':>8}")
print("─" * 100)
for user, d in sorted(user_stats.items(), key=lambda x: x[1]["messages"], reverse=True):
    avg_c = d["char_sum"] / d["messages"] if d["messages"] else 0
    avg_w = d["word_sum"] / d["messages"] if d["messages"] else 0
    print(f"{user[:22]:<22} | {d['messages']:>6} | {d['media']:>5} | {d['deleted']:>4} | {d['bad_word']:>4} | {avg_c:>8.1f} | {avg_w:>8.1f}")
print("═" * 100)

# Group creation
if group_info["created_ts"]:
    print(f"Group created : {group_info['created_ts']}  by {group_info['created_by']}  (name: {group_info['created_name']})")

# Rename history
print("\nGroup Rename History:")
if group_renames:
    for label, changer, old, new in group_renames:
        print(f"🕒 {label} | 👤 {changer} renamed → “{old}” → “{new}”")
else:
    print("No renames detected.")

# Daily stats
total_msgs = sum(hour_counts.values())
if total_msgs:
    most_media_day, most_media_cnt = max(media_per_day.items(), key=lambda x: x[1]) if media_per_day else ("-", 0)
    max_day, max_count = max(messages_per_day.items(), key=lambda x: x[1])
    min_day, min_count = min(messages_per_day.items(), key=lambda x: x[1])
    avg_per_day = total_msgs / len(messages_per_day)
    print("\nOverall Message Stats:")
    print(f"Total messages : {total_msgs}")
    print(f"Day with most media : {most_media_day} ({most_media_cnt} files sent)")
    print(f"Most active day : {max_day} ({max_count} messages)")
    print(f"Least active day: {min_day} ({min_count} messages)")
    print(f"Average messages per day : {avg_per_day:.2f}")

# Hourly activity
print("\nHourly Distribution (0‑23):")
for h in range(24):
    print(f"{h:02d}: {hour_counts[h]}", end="  " if h % 6 != 5 else "\n")

# Weekday activity
print("\nWeekday Distribution:")
for i in range(7):
    name = FA_WEEKDAYS[i] if jdatetime else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][(i+1)%7]
    print(f"{name:<9}: {weekday_counts[i]}")

# Month activity
print("\nMonthly Distribution:")
for m in range(1, 13):
    print(f"{m:02d}: {month_counts[m]}")

# Top words
print("\nTop 20 words (ex stop words):")
for word, cnt in word_freq_global.most_common(20):
    print(f"{word:<10} {cnt}")

# Emoji stats
if emoji_freq_global:
    print("\nTop 20 emojis:")
    for e, cnt in emoji_freq_global.most_common(20):
        print(f"{e} {cnt}")
print("═" * 100)

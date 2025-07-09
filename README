# WhatsApp Group Analyzer

**WhatsApp Group Analyzer** is a simple and fun Python script for analyzing exported WhatsApp group chats. It provides detailed statistics per user, group activity trends, word and emoji usage, and more. It supports both Gregorian and Jalali (Shamsi) calendars for Persian users.

---

## Features

- Per-user message, media, deleted, and bad-word counts
- Jalali (Shamsi) and Gregorian date support
- Daily, hourly, weekday, and monthly activity stats
- Group creation and rename timeline
- Average message length (chars & words) per user
- First & last message timestamp per user
- Hour-of-day heatmap
- Weekday and monthly activity distribution
- Global top-N common words (stop-words removed)
- Emoji usage stats (overall & per user)
- Day with most media shared

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/whatsapp-group-analyzer.git
   cd whatsapp-group-analyzer
   ```

2. **Install dependencies:**
   ```sh
   pip install jdatetime emoji
   ```

---

## Usage

1. **Export your WhatsApp group chat:**
   - In WhatsApp, open the group chat.
   - Tap the group name > More > Export chat > Without media.
   - Save the exported `.txt` file (e.g., `Chats.txt`).

2. **Place the exported file:**
   - or update the `CHAT_FILE` variable in `script.py` to match your filename.
   - (Optional) Add `bad_words.txt` and `stop_words.txt` for custom filtering.

3. **Run the script:**
   ```sh
   python script.py
   ```

---

## Sample Output

```
════════════════════════════════════════════════════════════════════════════════════════════════════════════
USER SUMMARY (sorted by messages)

Name                   |   Msgs | Media | Del | Bad |  AvgChars |  AvgWords
──────────────────────────────────────────────────────────────────────────────────────────────────────────
Ali                    |    350 |    12 |   3 |   1 |     42.3 |      8.7
Sara                   |    210 |     5 |   0 |   0 |     38.1 |      7.9
Reza                   |    180 |     8 |   1 |   2 |     44.7 |      9.2
════════════════════════════════════════════════════════════════════════════════════════════════════════════
Group created : 1402/01/15  by Ali  (name: Family Group)

Group Rename History:
🕒 1402/03/10 | 👤 Sara renamed → “Family Group” → “Family & Friends”
🕒 1402/05/22 | 👤 Reza renamed → “Family & Friends” → “Our Family”

Overall Message Stats:
Total messages : 740
Day with most media : 1402/02/05 (6 files sent)
Most active day : 1402/01/20 (52 messages)
Least active day: 1402/04/01 (1 messages)
Average messages per day : 12.34

Hourly Distribution (0‑23):
00: 12  01: 8   02: 3   03: 0   04: 0   05: 0
06: 1   07: 2   08: 10  09: 18  10: 25  11: 30
12: 40  13: 50  14: 60  15: 70  16: 80  17: 90
18: 100 19: 80 20: 60 21: 40 22: 20 23: 10

Weekday Distribution:
شنبه      : 120
یکشنبه    : 110
دوشنبه    : 100
سه‌شنبه   : 90
چهارشنبه  : 80
پنج‌شنبه  : 140
جمعه      : 100

Monthly Distribution:
01: 120
02: 130
03: 110
04: 90
05: 140
06: 150
07: 0
08: 0
09: 0
10: 0
11: 0
12: 0

Top 20 words (ex stop words):
سلام        50
خوبی        30
دوست        25
خانواده     20
...
Top 20 emojis:
😂 15
❤️ 12
👍 10
...
════════════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## Customization

- **Bad words:** Add words (one per line) to `bad_words.txt` to count their usage.
- **Stop words:** Add common words to `stop_words.txt` (one per line, Persian or English) to exclude them from top word stats.

---

## License

MIT License

---

## Acknowledgements

- [jdatetime](https://github.com/slashmili/python-jalali)
- [emoji](https://github.com/carpedm20/emoji)

---

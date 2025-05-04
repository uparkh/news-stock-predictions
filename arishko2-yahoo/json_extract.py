import json
import csv
import os
from datetime import datetime

MONTH_MAP = {
    '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
    '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
    '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
}

# For month sorting
MONTH_ORDER = {v: i for i, v in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
)}

def extract_month(date_str):
    try:
        if not date_str or "No date found" in date_str:
            return None
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        return MONTH_MAP[dt.strftime("%m")]
    except Exception:
        try:
            parts = date_str.split("-")
            if len(parts) >= 2:
                month_num = parts[1].zfill(2)
                return MONTH_MAP.get(month_num)
        except Exception:
            pass
        return None

def read_json_files(input_dir):
    all_articles = []
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    print("\nFound JSON files:")
    for filename in json_files:
        print(f" - {filename}")

    for filename in json_files:
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            all_articles.extend(data)

    print(f"\nTotal records loaded: {len(all_articles)}")
    return all_articles

def write_csv(articles, output_csv):
    rows = []
    max_sentences = 0

    for article in articles:
        month = extract_month(article.get("date", ""))
        if not month:
            continue

        title = article.get("title", "").strip()
        content = article.get("article_content", "").strip()

        if not content:
            continue

        sentences = [s.strip() for s in content.split('\n') if s.strip()]
        max_sentences = max(max_sentences, len(sentences))

        row = [month, title] + sentences
        rows.append(row)

    rows.sort(key=lambda r: MONTH_ORDER.get(r[0], 99))

    headers = ["month", "title"] + [f"text{i}" for i in range(max_sentences)]

    for row in rows:
        row += [""] * (len(headers) - len(row))

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} records to {output_csv}")

if __name__ == "__main__":
    input_dir = "/Users/antanasrishko/scripts/cs410/news-stock-predictions/arishko2-yahoo/files"
    output_csv = "output.csv"
    articles = read_json_files(input_dir)
    write_csv(articles, output_csv)

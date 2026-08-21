import csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import os
import subprocess


# 清除螢幕的魔法
_ = subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)

# 1.準備爬蟲年分和url
year = 114
URL = "https://kmweb.moa.gov.tw/theme_data.php?theme=production_map&id=117"


# 2. 準備偽造的瀏覽器herder
# 2-1建立一個 Session 物件
session = requests.Session()

# 2-2. 準備偽造的瀏覽器herder，綁定在session上面
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
})


# 3.請求，發送get/post
# 第一個函數，爬蟲
def get_production_data(selected_year: int) -> list[dict[str, str]]:
    # 因為有年份的下拉列表，頁面原始碼顯示post，所以要用requests.post
    # 但是上面偽造的瀏覽器herder已經綁定在session上面，就不需要headers=headers了
    response = session.post(URL, data={"year": str(selected_year)})
    response.raise_for_status()
    response.encoding = response.apparent_encoding  # 因為該網站用utf-8編碼，直接寫成response.encoding = utf-8也行

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("label", string=lambda text: text and "各縣市鄉鎮產量" in text)
    if title is None:
        raise RuntimeError("找不到產量表格，請確認網站頁面結構是否變更。")

    table = title.find_parent("div", class_="bgblur3").find("table")
    if table is None:
        raise RuntimeError("找不到產量表格。")

    headers = [cell.get_text(" ", strip=True) for cell in table.select("thead tr:first-child th")]
    rows: list[dict[str, str]] = []
    for row in table.select("tbody tr"):
        cells = row.find_all("td")
        if len(cells) != len(headers):
            continue

        values = []
        for cell in cells:
            parts = [part.get_text(" ", strip=True) for part in cell.find_all("div")]
            values.append(parts[-1] if parts else cell.get_text(" ", strip=True))
        rows.append(dict(zip(headers, values)))

    return rows


# 第二個函數，存成csv
def save_csv(rows: list[dict[str, str]], output_file: Path) -> None:
    if not rows:
        raise RuntimeError("表格沒有資料列。")

    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    os.makedirs("csv", exist_ok=True)  # 如果 data 資料夾不存在就自動建立
    OUTPUT_FILE = Path(f"csv/coffee_production_{year}.csv")
    
    data = get_production_data(year)
    save_csv(data, OUTPUT_FILE)

    print(f"民國 {year} 年，共爬取 {len(data)} 筆資料：")
    for row in data:
        print(row)
    print(f"\n資料已儲存至：{OUTPUT_FILE}")
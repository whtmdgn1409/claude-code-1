"""
Analyze Ppomppu row structure to understand the HTML.
"""
import requests
from bs4 import BeautifulSoup

URL = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"

response = requests.get(URL, timeout=10)
response.encoding = "euc-kr"
soup = BeautifulSoup(response.text, "html.parser")

# Find the main table
table = soup.find("table", {"id": "revolution_main_table"})

if table:
    print("✅ Found table!")
    rows = table.find_all("tr")
    print(f"Total rows: {len(rows)}")
    print("\n" + "=" * 80)

    # Analyze first few data rows (skip header)
    for i, row in enumerate(rows[1:6]):  # Skip first row (header), show next 5
        print(f"\nRow {i+1}:")
        print("-" * 80)

        cells = row.find_all("td")
        print(f"Total cells: {len(cells)}")

        for j, cell in enumerate(cells):
            print(f"\n  Cell {j}:")
            print(f"    Class: {cell.get('class')}")
            print(f"    Text: {cell.get_text(strip=True)[:100]}")

            # Look for links
            links = cell.find_all("a")
            if links:
                for link in links:
                    print(f"    Link href: {link.get('href')}")
                    print(f"    Link text: {link.get_text(strip=True)[:50]}")

        print("=" * 80)
else:
    print("❌ Table not found")

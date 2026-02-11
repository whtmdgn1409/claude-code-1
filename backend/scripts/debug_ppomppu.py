"""
Debug script to inspect Ppomppu HTML structure.
"""
import requests
from bs4 import BeautifulSoup

URL = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"

print(f"Fetching: {URL}")
print("=" * 60)

try:
    response = requests.get(URL, timeout=10)
    response.encoding = "euc-kr"

    print(f"Status: {response.status_code}")
    print(f"Encoding: {response.encoding}")
    print("=" * 60)

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables
    tables = soup.find_all("table")
    print(f"\nFound {len(tables)} tables")

    for i, table in enumerate(tables[:5]):  # Show first 5 tables
        print(f"\nTable {i+1}:")
        print(f"  Classes: {table.get('class')}")
        print(f"  ID: {table.get('id')}")
        print(f"  Width: {table.get('width')}")

        # Show first row
        rows = table.find_all("tr")
        if rows:
            print(f"  Rows: {len(rows)}")
            first_row = rows[0] if len(rows) > 0 else None
            if first_row:
                cells = first_row.find_all(["td", "th"])
                print(f"  First row cells: {len(cells)}")
                if cells:
                    print(f"  First cell text: {cells[0].get_text(strip=True)[:50]}")

    # Look for specific elements
    print("\n" + "=" * 60)
    print("Looking for common board patterns...")

    # Look for list items
    list_items = soup.find_all("li", class_=lambda x: x and "list" in x.lower() if x else False)
    print(f"List items with 'list' class: {len(list_items)}")

    # Look for div containers
    divs = soup.find_all("div", class_=lambda x: x and any(word in x.lower() for word in ["list", "board", "table"]) if x else False)
    print(f"Divs with list/board/table class: {len(divs)}")

    # Save HTML for inspection
    with open("/tmp/ppomppu_debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"\n✅ HTML saved to /tmp/ppomppu_debug.html")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

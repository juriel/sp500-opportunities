import requests
from bs4 import BeautifulSoup
import pandas as pd

_URL = "https://www.slickcharts.com/sp500"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def get_sp500_components() -> pd.DataFrame:
    """
    Returns a DataFrame with S&P 500 components from slickcharts.com.

    Columns: rank, company, symbol, weight, price, change, pct_change
    """
    response = requests.get(_URL, headers=_HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "table"})
    if table is None:
        raise ValueError("Could not find the S&P 500 table on the page.")

    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cols = tr.find_all("td")
        if len(cols) < 7:
            continue

        rank = int(cols[0].get_text(strip=True))
        company = cols[1].get_text(strip=True)
        symbol = cols[2].get_text(strip=True)
        weight = float(cols[3].get_text(strip=True).replace("%", ""))

        price_span = cols[4].find("span")
        price = float(price_span.get_text(strip=True).replace(",", "")) if price_span else None

        change = cols[5].get_text(strip=True)
        pct_change = cols[6].get_text(strip=True)

        rows.append({
            "rank": rank,
            "company": company,
            "symbol": symbol,
            "weight": weight,
            "price": price,
            "change": _to_float(change),
            "pct_change": _to_float(pct_change),
        })

    return pd.DataFrame(rows)


def _to_float(value: str) -> float | None:
    try:
        return float(value.replace("%", "").replace(",", ""))
    except (ValueError, AttributeError):
        return None

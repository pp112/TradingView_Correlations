import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console


class TradingViewAPI:
    def __init__(self, cookies: dict):
        self.console = Console()
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        retry = Retry(
            total=5,                       
            backoff_factor=1,          
            status_forcelist=[429,500,502,503,504],
            allowed_methods=["GET","POST"] 
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_all_tickers(self):
        
        url = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/"
        }

        with open("tradingview/scanner_payload.json", encoding="utf-8") as f:
            payload = json.load(f)

        with self.console.status("[cyan]Получаем список всех тикеров...[/cyan]", spinner="bouncingBar"):
            response = self.session.post(url=url, headers=headers, json=payload)
            response.raise_for_status()
            data_response = response.json()
            all_tickers = [item["s"] for item in data_response["data"]]

        self.console.print("[bold green]✔ Получены тикеры[/bold green]")

        return all_tickers
    
    def add_tickers_to_list(self, tickers):

        base = "https://ru.tradingview.com/api/v1/symbols_list/colored/red"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://ru.tradingview.com",
            "Referer": "https://ru.tradingview.com/chart/RRGuoDgP"
        }

        symbols_data = [f"BYBIT:{ticker}" for ticker in tickers]

        watchlist_get_response = self.session.get(url=f"{base}?source=web", headers=headers)
        watchlist_get_response.raise_for_status()

        watchlist = watchlist_get_response.json()["symbols"]
        if watchlist:
            watchlist_remove_response = self.session.post(url=f"{base}/remove/?source=web", headers=headers, json=watchlist)
            watchlist_remove_response.raise_for_status()

        watchlist_add_response = self.session.post(url=f"{base}/append/?source=web", headers=headers, json=symbols_data)
        watchlist_add_response.raise_for_status()

    def close_session(self):
        self.session.close()

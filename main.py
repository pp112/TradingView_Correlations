from botasaurus.browser import browser, Driver
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
import time
import requests
import json

console = Console()

class TradingViewCorrs:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.cookies = {}
        self.all_tickers = []
        self.tickers_correlations = {}

    # -----------------------
    # Открыть TradingView
    # -----------------------
    def open_tradingview(self):
        with console.status("[green]Открываем TradingView...[/green]"):
            self.driver.get("https://ru.tradingview.com/chart/RRGuoDgP")
            self.cookies = self.driver.get_cookies_dict()
        console.print("[bold green]✔ Открыт TradingView[/bold green]")

    # Добавить тикеры в список
    def add_tickers_to_list(self, tickers):

        watchlist_get_url = "https://ru.tradingview.com/api/v1/symbols_list/colored/red?source=web"
        watchlist_add_url = "https://ru.tradingview.com/api/v1/symbols_list/colored/red/append/?source=web"
        watchlist_remove_url = "https://ru.tradingview.com/api/v1/symbols_list/colored/red/remove/?source=web"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://ru.tradingview.com",
            "Referer": "https://ru.tradingview.com/chart/RRGuoDgP"
        }

        cookies = self.driver.get_cookies_dict()

        symbols_data = [f"BYBIT:{tikcer}" for tikcer in tickers]

        watchlist_get_response = requests.get(url=watchlist_get_url, headers=headers, cookies=cookies)
        watchlist_get_response.raise_for_status()

        watchlist = watchlist_get_response.json()["symbols"]
        if watchlist:
            watchlist_remove_response = requests.post(url=watchlist_remove_url, headers=headers, 
                                                      cookies=cookies, json=watchlist)
            watchlist_remove_response.raise_for_status()

        watchlist_add_response = requests.post(url=watchlist_add_url, headers=headers, 
                                               cookies=cookies, json=symbols_data)
        watchlist_add_response.raise_for_status()

        self.driver.reload()

    # -----------------------
    # Добавить индикатор корреляции
    # -----------------------
    def activate_corr_indicator(self):
        with console.status("[yellow]Активируем индикатор корреляции...[/yellow]", spinner="line"):
            self.driver.enable_human_mode()

            indicators = self.driver.select_all(".sources-l31H9iuA .mainTitle-l31H9iuA")
            corr_exists = False

            for indicator in indicators:
                if indicator.text == "Корреляция":
                    corr_exists = True
                    continue

                self.driver.move_mouse_to_element(indicator)
                indicator.parent.parent.click("button[data-qa-id='legend-delete-action']")

            self.driver.disable_human_mode()

            if not corr_exists:
                self.driver.click("#header-toolbar-indicators button[data-name='show-favorite-indicators']")
                self.driver.get_element_with_exact_text("Корреляция").click()
        console.print("[bold green]✔ Индикатор активирован[/bold green]")
    
    # -----------------------
    # Получить все тикеры
    # -----------------------
    def get_all_tickers(self):

        all_tickers_get_url = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/"
        }

        with open("scanner_payload.json", encoding="utf-8") as f:
            payload = json.load(f)

        with console.status("[cyan]Получаем список всех тикеров...[/cyan]", spinner="bouncingBar"):
            response = requests.post(url=all_tickers_get_url, headers=headers, cookies=self.cookies, json=payload)
            response.raise_for_status()
            data_response = response.json()
            self.all_tickers = [item["s"] for item in data_response["data"]]
        console.print("[bold green]✔ Получены тикеры[/bold green]")

    # -----------------------
    # Получить корреляцию тикера
    # -----------------------
    def get_correlation(self):
        ticker = self.driver.select("[data-qa-id='details-element symbol']").text
        correlation = float(
            self.driver.select(".sources-l31H9iuA .valueValue-l31H9iuA").text.replace(",", ".").replace("−", "-")
        )
        self.tickers_correlations[ticker] = correlation
    
    # -----------------------
    # Сбор всех корреляций
    # -----------------------
    def collect_correlations(self):
        with console.status("[yellow]Подготавливаем тикеры...[/yellow]"):
            self.driver.click("button[data-name='screener-dialog-button']")
            
            template_name_screener = self.driver.select("div[data-qa-id='screen-title']")
            if template_name_screener.text != "Фьючерсы Bybit":
                template_name_screener.click()
                self.driver.get_element_with_exact_text("Фьючерсы Bybit").click()

            total_tickers = len(self.all_tickers)
            tickers = self.driver.select_all("tbody tr")
        console.print("[bold green]✔ Список тикеров готов[/bold green]")

        console.print(f"[magenta]Найдено {total_tickers} тикеров...[/magenta]")

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TextColumn("[bright_green]{task.completed}[/bright_green]/[yellow]{task.total}[/yellow]"),
            TextColumn("[bright_green]{task.percentage:>3.0f}%[/bright_green]"),
            TimeRemainingColumn()
        )
        
        with progress:
            task = progress.add_task("Собираем корреляции", total=total_tickers)
            i = 0
            while i < len(tickers):
                tickers[i].click()
                self.get_correlation()
                i += 1
                progress.update(task, advance=1)

                if i >= len(tickers) - 5:
                    tickers = self.driver.select_all("tbody tr")
                
                if len(self.tickers_correlations) == total_tickers:
                    break

        console.print(Panel.fit(
            "🎯 [bold white]Все корреляции собраны![/bold white] 🎯",
            border_style="bold green",
            style="on dark_green",
            title="[bold yellow]Завершено[/bold yellow]"
        ))
        
    # -----------------------
    # Pipeline: корреляции
    # -----------------------
    def get_correlations(self):
        self.open_tradingview()
        self.get_all_tickers()
        self.activate_corr_indicator()
        self.collect_correlations()

        return self.tickers_correlations


@browser(
    output=None,
    profile="TradingviewProfile",
    wait_for_complete_page_load=True
)
def main(driver: Driver, data):
    tv = TradingViewCorrs(driver)
    tickers_correlations = tv.get_correlations()
    print(tickers_correlations)
    
main()

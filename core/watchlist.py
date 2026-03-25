from rich.console import Console

from tradingview import TradingViewAPI
from ui.correlation_utils import filter_low_correlations
from ui import Prompter


class Watchlist:
    def __init__(self, tickers, tradingview_api: TradingViewAPI):
        self.console = Console()
        self.prompter = Prompter()
        self.tickers = tickers
        self.tradingview_api = tradingview_api

    def add_low_corr_tickers_to_tradingview(self, threshold):

        self.console.print(f"[cyan]Найдено {len(self.tickers)} тикеров с корреляцией ниже {threshold}[/cyan]")

        batch_size = 30
        total = len(self.tickers)

        for i in range(0, total, batch_size):
            ticker_batch = self.tickers[i:i + batch_size]
            start = i + 1
            end = i + len(ticker_batch)

            with self.console.status(f"[cyan]Добавляем {start}-{end} из {len(self.tickers)} тикеров в список TradingView...[/cyan]", spinner="line"):
                self.tradingview_api.add_tickers_to_list(ticker_batch)
            
            if i + batch_size >= total:
                self.console.print(f"[bold green]Все {total} тикеров были успешно добавлены в список![/bold green]")
                break
            
            self.console.print(f"[yellow]Тикеры {start}-{end} добавлены в список.[/yellow]")

            action = self.prompter.select_next_action()

            if action == "skip":
                self.console.print("[red]Добавление тикеров остановлено пользователем[/red]")
                break

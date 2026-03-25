import os
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.watchlist import Watchlist
from ui.correlation_utils import filter_low_correlations, sort_correlations, save_excel, save_txt
from tradingview import TradingViewAPI
from ui import Prompter


class UI:
    def __init__(self, tickers_correlations: dict, tradingview_api: TradingViewAPI):
        self.console = Console()
        self.prompter = Prompter()
        self.default_tickers_correlations = tickers_correlations
        self.threshold = None
        self.sort_order = None
        self.export_tickers_correlations = tickers_correlations.copy()
        self.tradingview_api = tradingview_api

    def prompt_user_settings(self):
        self.threshold = self.prompter.select_threshold()

        self.sort_order = self.prompter.select_sort_order()
    
    def apply_user_settings(self):
        self.export_tickers_correlations = filter_low_correlations(self.export_tickers_correlations,
                                                                   self.threshold)
        
        self.export_tickers_correlations = sort_correlations(self.export_tickers_correlations, 
                                                             self.sort_order)

    def show_results_table(self):
        show_table, filter_mode = self._prompt_show_table()
        
        if not show_table:
            return
        
        if not filter_mode:
            data = self.export_tickers_correlations
        else:
            data = sort_correlations(self.default_tickers_correlations, self.sort_order)

        table = Table(title=f"\nКорреляции тикеров ({len(data)})", show_lines=True)
        table.add_column("Тикер", justify="center", style="cyan", no_wrap=True)
        table.add_column("Корреляция", justify="center")
        
        for ticker, corr in data.items():
            table.add_row(ticker, f"[green]{corr}[/green]")

        self.console.print(table)

    def save_results(self):
        save_folder = "results"
        os.makedirs(save_folder, exist_ok=True)
        file_name = f"{save_folder}/Корреляция_{datetime.now():%d.%m.%y_%H-%M}"

        with self.console.status("[green]Сохраняем результаты...[/green]"):
            save_txt(self.export_tickers_correlations, file_name)
            save_excel(self.export_tickers_correlations, file_name, self.threshold)

        self.console.print(Panel.fit(
            f"🎯 [bold white]Результаты сохранены![/bold white]\n\n"
            f"[cyan]Файлы:[/cyan]\n"
            f"• {file_name}.txt\n"
            f"• {file_name}.xlsx",
            border_style="bold green"
        ))

    def add_tickers_to_tradingview(self):
        if self.prompter.confirm_add_tickers_to_watchlist:
            tickers = list(self.export_tickers_correlations)
            watchlist = Watchlist(tickers, self.tradingview_api)
            watchlist.add_low_corr_tickers_to_tradingview(self.threshold)

    def press_enter_to_finish(self):
        input("\nНажмите Enter для завершения...")

    def _prompt_show_table(self):
        show_table = self.prompter.confirm_show_table()

        if not show_table:
            return (False, False)
        
        filter_mode = self.prompter.select_filter_mode()

        if filter_mode:
            return (True, True)
        else:
            return (True, False)

    def display_results(self):
        self.console.print(f"[cyan]{'═'*25}[/cyan] [bold white]Вывод результатов[/bold white] [cyan]{'═'*25}[/cyan]")

        self.prompt_user_settings()
        self.apply_user_settings()
        self.save_results()
        self.show_results_table()
        self.add_tickers_to_tradingview()

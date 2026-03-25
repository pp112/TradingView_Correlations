from botasaurus.browser import Driver
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.console import Console

from ui import Prompter


class TickerCorrelationCollector:
    def __init__(self, driver: Driver, all_tickers):
        self.driver = driver
        self.console = Console()
        self.prompter = Prompter()
        self.all_tickers = all_tickers
        self.tickers_correlations = {}
    
    def collect_correlations(self):
        self._prepare_screener()
        total_tickers = len(self.all_tickers)
        
        self.console.print(f"[magenta]Найдено {total_tickers} тикеров...[/magenta]")
        
        self._iterate_tickers(total_tickers)
        self.prompter.show_completion_message()

        return self.tickers_correlations

    def _prepare_screener(self):
        with self.console.status("[yellow]Подготавливаем тикеры...[/yellow]"):
            self.driver.click("button[data-name='screener-dialog-button']")
            
            template_name_screener = self.driver.select("div[data-qa-id='screen-title']")
            if template_name_screener.text != "Фьючерсы Bybit":
                template_name_screener.click()
                self.driver.get_element_with_exact_text("Фьючерсы Bybit").click()
    
        self.console.print("[bold green]✔ Список тикеров готов[/bold green]")

    def _iterate_tickers(self, total_tickers):
        """Собирает корреляции для всех тикеров с отображением прогресса."""
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
            tickers = self.driver.select_all("tbody tr")
            while True:
                for ticker in tickers:
                    ticker.click()
                    self._get_correlation()
                    progress.update(task, advance=1)
                    i += 1

                tickers = self.driver.select_all("tbody tr")[i:]

                if i == total_tickers:
                    break

    def _get_correlation(self):
        ticker = self.driver.select("#header-toolbar-symbol-search").text
        try:
            correlation = float(
                self.driver.select(".sources-l31H9iuA .valueValue-l31H9iuA").text.replace(",", ".").replace("−", "-")
            )
        except ValueError:
            return
        self.tickers_correlations[ticker] = correlation

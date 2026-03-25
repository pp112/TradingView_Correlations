from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel


class Prompter:
    def __init__(self):
        self.console = Console()
        self.threshold = None

    def select_threshold(self):
        self.threshold = float(inquirer.select(
            message="Выберите порог корреляции:",
            choices=[f"{x/10:.1f}" for x in range(1, 11)],
            default="0.5",
            qmark="", amark=""
        ).execute())
        return self.threshold
    
    def select_sort_order(self):
        return inquirer.select(
            message="Сортировка:",
            choices=[
                {"name": "без сортировки", "value": None},
                {"name": "сначала низкая корреляция", "value": "asc"},
                {"name": "сначала высокая корреляция", "value": "desc"},
            ],
            default=None,
            qmark="", amark=""
        ).execute()
    
    def confirm_add_tickers_to_watchlist(self):
        return inquirer.select(
            message=f"Добавить тикеры с корреляцией ниже {self.threshold} в список TradingView?",
            choices=[{"name": "Да", "value": True}, {"name": "Нет", "value": False}],
            default=True,
            qmark="", amark=""
        ).execute()
    
    def confirm_show_table(self):
        return inquirer.select(
            message="Показать таблицу корреляций?",
            choices=[{"name": "Да", "value": True}, {"name": "Нет", "value": False}],
            default=True,
            qmark="", amark=""
        ).execute()
    
    def select_filter_mode(self):
        return inquirer.select(
            message=f"Все или только с корреляцией ниже {self.threshold}?",
            choices=[{"name": f"Ниже {self.threshold}", "value": False}, {"name": "Все", "value": True}],
            default=False,
            qmark="", amark=""
        ).execute()
    
    def select_next_action(self):
        return inquirer.select(
            message="Продолжить добавление следующих тикеров?",
            choices=[
                {"name": "Продолжить", "value": "continue"}, 
                {"name": "Пропустить оставшиеся", "value": "skip"}
            ],
            default="continue",
            qmark="", amark=""
        ).execute()
    
    def show_captcha_info(self):
        self.console.print(
            "[bright_yellow]" \
            "Вышла капча. Откройте изображение [underline]captcha_image.png[/underline] и введите номера нужных изображений через пробел.\n"
            "Может быть несколько капчей. В таком случае изображение обновится для повторного ввода номеров.\n"
            "Пустой ответ - если изображение прорисовано не полностью.\n"
            "0 - если изображение пустое.\n"
            "y - подтвердить капчу."
            "[/bright_yellow]"
        )

    def show_completion_message(self):
        print()
        self.console.print(Panel.fit(
            "🎯 [bold white]Все корреляции собраны![/bold white] 🎯",
            border_style="bold green",
            style="on dark_green",
            title="[bold yellow]Завершено[/bold yellow]"
        ))
        print()
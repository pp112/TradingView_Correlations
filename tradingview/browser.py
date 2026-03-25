from enum import Enum
import shutil
import time

from botasaurus.browser import Driver
from rich.console import Console

from .captcha_solver import CaptchaSolver


class AuthResult(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    INVALID = "invalid"


class TradingViewBrowser:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.console = Console()
  
    def open_tradingview(self):
        with self.console.status("[green]Открываем TradingView...[/green]"):
            self.driver.get("https://ru.tradingview.com/chart/RRGuoDgP")

        self._login_tradingview()

        self.console.print("[bold green]✔ TradingView готов к работе[/bold green]")

    def get_cookies(self):
        return self.driver.get_cookies_dict()
    
    def _login_tradingview(self):
        login_btn = self.driver.select(".linkButton-dfXNuaqf")
        if login_btn is None:
            return

        self.console.print("[bold bright_blue]Авторизация в аккаунт TradingView[/bold bright_blue]")

        username, password = self._get_credentials()

        while True:
            self._submit_credentials(username, password)
            result = self._handle_auth_problems()

            if result == AuthResult.SUCCESS:
                break
            elif result == AuthResult.INVALID:
                username, password = self._get_credentials()

    def _get_credentials(self):
        username = input("Введите email: ")
        password = input("Введите пароль: ")
        return username, password

    def _submit_credentials(self, username, password):
        self.driver.click(".linkButton-dfXNuaqf")
        self.driver.click("button[name='Email']")

        with self.console.status("[cyan]Выполняем авторизацию...[/cyan]", spinner="dots"):
            self.driver.type("#id_username", username)
            self.driver.type("#id_password", password)
            self.driver.click("button[data-overflow-tooltip-text='Войти']")

    def _handle_auth_problems(self):
        problem_elem = self.driver.select(".mainProblem-TCHLKPuQ")
                        
        if problem_elem is None:
            with self.console.status("[cyan]Авторизация прошла успешно, загружаем TradingView...[/cyan]", spinner="dots"):
                self.driver.reload()
            return AuthResult.SUCCESS
        
        elif "Неправильное" in problem_elem.text:
            self.console.print("[bright_red]Неверный логин или пароль. Попробуйте снова.[/bright_red]")
            self.driver.reload()
            return AuthResult.INVALID

        elif "CAPTCHA" in problem_elem.text:
            if CaptchaSolver(self.driver).solve_captcha():
                self.driver.click("button[data-overflow-tooltip-text='Войти']")
                shutil.rmtree("output", ignore_errors=True)
                time.sleep(1.5)
            else:
                self.console.print("[bright_red]Таймер капчи истек. Пробуем заново...[/bright_red]")
                self.driver.reload()
            return AuthResult.RETRY

    def activate_corr_indicator(self):
        with self.console.status("[yellow]Активируем индикатор корреляции...[/yellow]", spinner="line"):
            self.driver.enable_human_mode()

            selector = ".sources-l31H9iuA .mainTitle-l31H9iuA"
            indicators = self.driver.select_all(selector)
            corr_exists = False

            for indicator in indicators:
                if indicator.text == "Корреляция":
                    corr_exists = True
                    continue
                
                self.driver.move_mouse_to_element(selector)
                indicator.parent.parent.click("button[data-qa-id='legend-delete-action']")

            self.driver.disable_human_mode()

            if not corr_exists:
                self.driver.click("#header-toolbar-indicators button[data-name='show-favorite-indicators']")
                self.driver.get_element_with_exact_text("Корреляция").click()

        self.console.print("[bold green]✔ Индикатор активирован[/bold green]")
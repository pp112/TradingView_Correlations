import os
import time
from contextlib import redirect_stdout

from rich.console import Console
from PIL import Image

from ui import Prompter


class CaptchaSolver:
    def __init__(self, driver):
        self.driver = driver
        self.console = Console()
        self.prompter = Prompter()

    def solve_captcha(self):
        """Обработка reCAPTCHA через пользовательский ввод."""
        self.prompter.show_captcha_info()

        captcha_frame = self.driver.select_iframe("iframe[title='reCAPTCHA']")
        captcha_frame.click("#rc-anchor-container")
        path_image = "output/screenshots/captcha_image.png"
        is_first_iteration = True

        while True:
            captcha_images = self.driver.select_iframe("[src*='bframe']").select("#rc-imageselect")
            self._get_captcha_image(path_image)
                        
            if not is_first_iteration:
                self.console.print("[bright_yellow]Изображение обновлено[/bright_yellow]")
            else:
                is_first_iteration = False

            user_input = input("Введите номера картинок: ")

            if user_input.lower() == "y":
                captcha_images.click(".rc-button-default")
                time.sleep(1.5)
                checkbox = captcha_frame.select("#recaptcha-anchor").get_attribute("aria-checked") == "true"
                if checkbox:
                    break
                else:
                    time.sleep(2)
            
            elif user_input == "0":
                self.console.print("[bright_yellow]Перезагрузка авторизации...[/bright_yellow]")
                return False

            elif user_input:
                self._click_captcha_images(captcha_images, user_input)
                time.sleep(1)

        self.console.print("[bold green]✔ Капча пройдена[/bold green]")
        return True

    def _get_captcha_image(self, path_image):
        """Сохраняет скриншот и обрезает его по расположению CAPTCHA."""
        filename = "captcha_image"
        self._save_screenshot_silent(filename)
        rect_captcha = self.driver.select("div:has(iframe[src*='bframe'])").get_bounding_rect()
        image = Image.open(path_image)
        cropped = image.crop((
            rect_captcha["x"],
            rect_captcha["y"],
            rect_captcha["x"] + rect_captcha["width"],
            rect_captcha["y"] + rect_captcha["height"]
        ))
        cropped.save(path_image)

    def _save_screenshot_silent(self, filename):
        """Сохраняет скриншот без вывода в терминал"""
        with open(os.devnull, "w") as f, redirect_stdout(f):
            self.driver.save_screenshot(filename)

    def _click_captcha_images(self, captcha_images, user_input):
        """Кликает по выбранным картинкам в CAPTCHA."""
        numbers = user_input.split(" ")
        try:
            for number in numbers:
                captcha_images.click(f"[id='{int(number) - 1}']")
                time.sleep(0.5)
        except ValueError:
            self.console.print("[red]Неккоректный ввод, попробуйте снова.[/red]")
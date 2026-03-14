from botasaurus.browser import browser, Driver
import time
import requests
import json


class TradingViewCorrs:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.cookies = {}
        self.all_tickers = []
        self.tickers_correlations = {}

    # Открыть TradingView
    def open_tradingview(self):
        self.driver.get("https://ru.tradingview.com/chart/RRGuoDgP")
        self.cookies = self.driver.get_cookies_dict()

    # Добавить индикатор корреляции
    def activate_corr_indicator(self):
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
    
    # Получить все тикеры в TradingView
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

        all_tickers_get_response = requests.post(url=all_tickers_get_url, headers=headers, 
                                                 cookies=self.cookies, json=payload)
        all_tickers_get_response.raise_for_status()
        data_response = all_tickers_get_response.json()
        
        self.all_tickers = [item["s"] for item in data_response["data"]]

    # Получить корреляцию с графика
    def get_correlation(self):
        ticker = self.driver.select("[data-qa-id='details-element symbol']").text
        correlation = float(
            self.driver.select(".sources-l31H9iuA .valueValue-l31H9iuA").text.replace(",", ".").replace("−", "-")
        )
        self.tickers_correlations[ticker] = correlation
    
    # Пройтись по списку добавленных тикеров и собрать корреляции
    def collect_correlations(self):
        self.driver.click("button[data-name='screener-dialog-button']")
        
        template_name_screener = self.driver.select("div[data-qa-id='screen-title']")
        if template_name_screener.text != "Фьючерсы Bybit":
            template_name_screener.click()
            self.driver.get_element_with_exact_text("Фьючерсы Bybit").click()

        total_tickers = len(self.all_tickers)
        tickers = self.driver.select_all("tbody tr")
        i = 0

        while i < len(tickers):
            ticker = tickers[i]
            ticker.click()
            self.get_correlation()

            i += 1

            if i >= len(tickers) - 5:
                tickers = self.driver.select_all("tbody tr")
            
            if len(self.tickers_correlations) == total_tickers:
                break

    # Собрать все корреляции
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

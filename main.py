from botasaurus.browser import browser, Driver
import time
import requests
import json


class TradingViewParser:
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

        symbols_data = [f"BYBIT:{tikcer}" for tikcer in tickers]

        watchlist_get_response = requests.get(url=watchlist_get_url, headers=headers, cookies=self.cookies)
        watchlist_get_response.raise_for_status()

        watchlist = watchlist_get_response.json()["symbols"]
        if watchlist:
            watchlist_remove_response = requests.post(url=watchlist_remove_url, headers=headers, 
                                                      cookies=self.cookies, json=watchlist)
            watchlist_remove_response.raise_for_status()

        watchlist_add_response = requests.post(url=watchlist_add_url, headers=headers, 
                                               cookies=self.cookies, json=symbols_data)
        watchlist_add_response.raise_for_status()

        self.driver.reload()

    # Пройтись по списку добавленных тикеров и собрать корреляции
    def collect_correlations_from_watchlist(self):
        tickers_in_watchlist = self.driver.select_all(".listContainer-MgF6KBas .firstItem-RsFlttSS")
        ticker_coord = []

        for el in tickers_in_watchlist:
            rect = el.get_bounding_rect()
            ticker_coord.append(rect["center"])

        for x, y in ticker_coord:
            self.driver.click_at_point(int(x), int(y))
            self.get_correlation()
        # TODO: Пролистывание списка

    # Получить корреляцию с графика
    def get_correlation(self):
        ticker = self.driver.select("[data-qa-id='details-element symbol']").text
        correlation = float(
            self.driver.select(".sources-l31H9iuA .valueValue-l31H9iuA").text.replace(",", ".").replace("−", "-")
        )
        self.tickers_correlations[ticker] = correlation

    # Проход по тикерам
    def process_tickers(self):
        batch_size = 30
        for i in range(0, len(self.all_tickers), batch_size):
        
            ticker_batch = self.all_tickers[i:i + batch_size]

            self.add_tickers_to_list(ticker_batch)
            self.collect_correlations_from_watchlist()
    
    # Собрать все корреляции
    def collect_all_correlations(self):
        self.open_tradingview()
        self.get_all_tickers()
        self.activate_corr_indicator()
        self.process_tickers()

        return self.tickers_correlations


@browser(
    output=None,
    profile="TradingviewProfile",
    wait_for_complete_page_load=True
)
def main(driver: Driver, data):
    tv = TradingViewParser(driver)
    tickers_correlations = tv.collect_all_correlations()
    print(tickers_correlations)
    
main()

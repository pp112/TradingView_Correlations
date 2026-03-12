from botasaurus.browser import browser, Driver
import time

class TradingViewParser:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.all_tickers = []
        self.tickers_correlations = {}

    # Открыть TradingView
    def open_tradingview(self):
        self.driver.get("https://ru.tradingview.com/chart/RRGuoDgP")

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
        self.driver.click("button[data-name='add-symbol-button']")
        filters = self.driver.select_all("button[data-qa-id='ss-filter-select-button']")

        if filters[0].text != "Bybit":
            filters[0].click()
            self.driver.type(".input-qm7Rg5MB", "Bybit")
            self.driver.select(".wrap-IxKZEhmO").click()

        if filters[1].text != "Своп":
            filters[1].click()
            self.driver.click("div[aria-label='Своп']")
        
        # Сбор тикеров
        prev_height = 0

        while True:
            self.driver.select(".scrollContainer-dlewR1s1").scroll_to_bottom()

            height = self.driver.select(".listContainer-dlewR1s1").get_bounding_rect()["height"]
            if height == prev_height:
                break

            prev_height = height
        
        self.all_tickers = self.driver.select_all(".description-oRSs8UQo")
        self.all_tickers = [t.text for t in self.all_tickers if t.text.endswith("USDT.P")]

        self.driver.click("button[data-qa-id='close']")

    # Добавить тикеры в список
    def add_tickers_to_list(self, tickers):
        self.driver.click("button[data-name='watchlists-button']")
        self.driver.get_element_with_exact_text("Очистить список").click()
        self.driver.click("button[data-qa-id='yes-btn']")
        
        self.driver.click("button[data-name='add-symbol-button']")
        for ticker in self.tickers_:
            ticker.click()

        for ticker in tickers:
            self.driver.type("input[data-qa-id='symbol-search-input']", ticker)
            self.driver.click(".listContainer-dlewR1s1 .descriptionCell-oRSs8UQo")
            self.driver.click("button[aria-label='Очистить']")
        
        self.driver.click("button[data-qa-id='close']")

    # Пройтись по списку добавленных тикеров и собрать корреляции
    def collect_correlations_from_watchlist(self):
        tickers_in_watchlist = self.driver.select_all(".listContainer-MgF6KBas .firstItem-RsFlttSS")
        
        self.driver.enable_human_mode()

        for ticker in tickers_in_watchlist:
            ticker.click()
            self.get_correlation()
        
        self.driver.disable_human_mode()

    # Получить корреляцию с графика
    def get_correlation(self):
        ticker = self.driver.select("[data-qa-id='details-element symbol']").text
        correlation = float(
            self.driver.select(".sources-l31H9iuA .valueValue-l31H9iuA").text.replace(",", ".")
        )
        self.tickers_correlations[ticker] = correlation

    # Проход по тикерам
    def process_tickers(self):
        batch_size = 30
        self.add_tickers_to_list(self.tickers_)
        # for i in range(0, len(self.all_tickers), batch_size):
        
        #     ticker_batch = self.all_tickers[i:i + batch_size]

        #     self.add_tickers_to_list(ticker_batch)
        #     self.collect_correlations_from_watchlist()
    
    # Собрать все корреляции
    def collect_all_correlations(self):
        self.open_tradingview()
        self.get_all_tickers()
        # self.activate_corr_indicator()
        # self.process_tickers()

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

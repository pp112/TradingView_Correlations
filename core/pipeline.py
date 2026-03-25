from botasaurus.browser import Driver

from tradingview import TradingViewBrowser, TradingViewAPI
from core import TickerCorrelationCollector
from ui import UI


class Pipeline:
    def __init__(self, driver: Driver):
        self.driver = driver

    def run(self, show_ui: bool):
        tradingview_browser = TradingViewBrowser(self.driver)
        tradingview_browser.open_tradingview()
        cookies = tradingview_browser.get_cookies()

        tradingview_api = TradingViewAPI(cookies)
        all_tickers = tradingview_api.get_all_tickers()

        tradingview_browser.activate_corr_indicator()

        collector = TickerCorrelationCollector(self.driver, all_tickers)
        tickers_correlations = collector.collect_correlations()

        if show_ui:
            ui = UI(tickers_correlations, tradingview_api)
            ui.display_results()
            ui.press_enter_to_finish()

        tradingview_api.close_session()

        return tickers_correlations

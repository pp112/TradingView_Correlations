from botasaurus.browser import browser, Driver
from botasaurus.window_size import WindowSize

from core.pipeline import Pipeline


class CorrelationsCollector:
    def run(self, show_ui: bool = True):
        @browser(
            output=None, 
            profile="TradingviewProfile",
            wait_for_complete_page_load=True,
            window_size=WindowSize.window_size_1920_1080
        )
        def _run_browser(driver: Driver, data):
            pipeline = Pipeline(driver)
            return pipeline.run(show_ui)
        
        return _run_browser()
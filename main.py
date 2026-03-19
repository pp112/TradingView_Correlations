from botasaurus.browser import browser
from tradingview_corrs import TradingViewCorrs
from botasaurus.window_size import WindowSize

@browser(
    output=None, 
    profile="TradingviewProfile",
    wait_for_complete_page_load=True,
    window_size=WindowSize.window_size_1920_1080
)
def main(driver, data):
    tv = TradingViewCorrs(driver)
    tv.get_correlations()


if __name__ == "__main__":
    main()
from botasaurus.browser import browser
from tradingview_corrs import TradingViewCorrs

@browser(
    output=None, 
    profile="TradingviewProfile",
    wait_for_complete_page_load=True
)
def main(driver, data):
    tv = TradingViewCorrs(driver)
    tv.get_correlations()


if __name__ == "__main__":
    main()
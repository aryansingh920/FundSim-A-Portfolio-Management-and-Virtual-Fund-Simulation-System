# initialization.py
import random
import string
from typing import Tuple, Set

from faker import Faker
from model import (
    Stock,
    PriceTradingInfo,
    FundamentalMetrics,
    VolatilityRisk,
    MarketIndicators
)
from constants import SECTORS


class StockDataInitializer:
    def __init__(self):
        """
        Initialize the stock data generator with tracking sets and faker
        """
        self.generated_tickers: Set[str] = set()
        self.fake = Faker()

    def generate_unique_ticker(self) -> str:
        """
        Generate a unique stock ticker
        
        Returns:
            str: A unique stock ticker
        """
        while True:
            # Generate a random length between 3 and 6
            length = random.randint(3, 6)
            ticker = ''.join(random.choices(string.ascii_uppercase, k=length))
            if ticker not in self.generated_tickers:
                self.generated_tickers.add(ticker)
                return ticker

    def generate_market_cap(self) -> float:
        """
        Generate market capitalization based on weighted random choice
        
        Returns:
            float: Market capitalization
        """
        # Category weights:
        #  - Small-Cap: ~ $100M to $2B
        #  - Mid-Cap:   ~ $2B to $10B
        #  - Large-Cap: ~ $10B to $2T
        cap_category = random.choices(
            ["Small-Cap", "Mid-Cap", "Large-Cap"],
            weights=[0.6, 0.39, 0.01],
            k=1
        )[0]

        if cap_category == "Small-Cap":
            return random.uniform(1e8, 2e9)
        elif cap_category == "Mid-Cap":
            return random.uniform(2e9, 10e9)
        else:
            return random.uniform(10e9, 2e12)

    def cap_category(self, market_cap: float) -> str:
        """
        Determine market cap category
        
        Args:
            market_cap (float): Market capitalization
        
        Returns:
            str: Market cap category
        """
        if market_cap > 10**10:  # > $10B
            return "Large-Cap"
        elif market_cap > 2 * 10**9:  # > $2B
            return "Mid-Cap"
        return "Small-Cap"

    def _generate_stock_basic_info(self) -> Tuple[Stock, float]:
        """
        Generate basic stock information
        
        Returns:
            Tuple of Stock object and market cap
        """
        ticker = self.generate_unique_ticker()
        company_name = self.fake.company()
        sector = random.choice(SECTORS)
        market_cap = self.generate_market_cap()
        # Shares outstanding roughly scales with market cap (but still random)
        # Large-cap companies generally have more shares outstanding.
        if market_cap > 1e11:
            # Very large: ~1B to 20B shares
            shares_outstanding = random.randint(10**9, 2 * 10**10)
        elif market_cap > 5e9:
            # Mid-size: ~100M to 5B shares
            shares_outstanding = random.randint(10**8, 5 * 10**9)
        else:
            # Small: ~10M to 1B shares
            shares_outstanding = random.randint(10**7, 10**9)

        stock = Stock(
            ticker=ticker,
            company_name=company_name,
            sector=sector,
            market_cap=round(market_cap, 2),
            cap_category=self.cap_category(market_cap),
            shares_outstanding=shares_outstanding
        )

        return stock, market_cap

    def _generate_price_trading_info(self, ticker: str, current_price: float) -> PriceTradingInfo:
        """
        Generate price and trading information
        
        Args:
            ticker (str): Stock ticker
            current_price (float): Current stock price
        
        Returns:
            PriceTradingInfo object
        """
        open_price = round(current_price * random.uniform(0.98, 1.02), 2)
        close_price = current_price
        day_high = round(current_price * random.uniform(1.01, 1.05), 2)
        day_low = round(current_price * random.uniform(0.95, 0.99), 2)
        week_52_high = round(current_price * random.uniform(1.2, 1.5), 2)
        week_52_low = round(current_price * random.uniform(0.5, 0.8), 2)
        trading_volume = random.randint(10**5, 10**7)  # 100K to 10M shares
        average_volume = int(trading_volume * random.uniform(0.8, 1.2))

        return PriceTradingInfo(
            ticker=ticker,
            current_price=current_price,
            open_price=open_price,
            close_price=close_price,
            day_high=day_high,
            day_low=day_low,
            week_52_high=week_52_high,
            week_52_low=week_52_low,
            trading_volume=trading_volume,
            average_volume=average_volume
        )

    def _generate_fundamental_metrics(self, ticker: str, current_price: float, market_cap: float, shares_outstanding: int) -> FundamentalMetrics:
        """
        Generate fundamental metrics with more logical consistency:
        - EPS derived randomly, then net income = EPS * shares_outstanding
        - P/E calculated from price and EPS
        - Revenue growth depends on market cap category
        """
        eps = round(random.uniform(0.5, 15), 2)
        net_income = round(eps * shares_outstanding, 2)
        price_to_earnings = round(current_price / eps, 2)

        # Dividend yield random, but could skew if large cap is chosen:
        # Large-cap might have higher chance of dividends.
        # For simplicity, keep it uniform for now.
        dividend_yield = round(random.uniform(0, 5), 2)

        roe = round(random.uniform(5, 30), 2)
        debt_to_equity = round(random.uniform(0.1, 2.5), 2)

        # Adjust revenue growth expectations by cap category
        cap_cat = self.cap_category(market_cap)
        if cap_cat == "Large-Cap":
            # More mature, stable growth
            revenue_growth = round(random.uniform(1, 10), 2)
        elif cap_cat == "Mid-Cap":
            revenue_growth = round(random.uniform(5, 15), 2)
        else:
            # Smaller, more growth potential
            revenue_growth = round(random.uniform(10, 30), 2)

        return FundamentalMetrics(
            ticker=ticker,
            earnings_per_share=eps,
            price_to_earnings=price_to_earnings,
            dividend_yield=dividend_yield,
            return_on_equity=roe,
            debt_to_equity=debt_to_equity,
            revenue_growth=revenue_growth,
            net_income=net_income
        )

    def _generate_volatility_risk(self, ticker: str, cap_cat: str) -> VolatilityRisk:
        """
        Generate volatility and risk metrics.
        - Large-Cap: Lower beta and volatility
        - Small-Cap: Higher beta and volatility
        """
        if cap_cat == "Large-Cap":
            beta = round(random.uniform(0.5, 1.2), 2)
            standard_deviation = round(random.uniform(5, 15), 2)  # percentage
        elif cap_cat == "Mid-Cap":
            beta = round(random.uniform(0.7, 1.5), 2)
            standard_deviation = round(random.uniform(10, 25), 2)
        else:
            beta = round(random.uniform(1.0, 2.0), 2)
            standard_deviation = round(random.uniform(15, 30), 2)

        sharpe_ratio = round(random.uniform(-1, 3), 2)

        return VolatilityRisk(
            ticker=ticker,
            beta=beta,
            standard_deviation=standard_deviation,
            sharpe_ratio=sharpe_ratio
        )

    def _generate_market_indicators(self, ticker: str, current_price: float) -> MarketIndicators:
        """
        Generate market sentiment and indicators.
        Keep these random for initialization.
        """
        rsi = random.randint(10, 90)
        moving_avg_50 = round(current_price * random.uniform(0.9, 1.1), 2)
        moving_avg_200 = round(current_price * random.uniform(0.8, 1.2), 2)
        macd = random.choice(["Positive", "Negative", "Neutral"])
        analyst_rating = random.choice(
            ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])

        return MarketIndicators(
            ticker=ticker,
            RSI=rsi,
            moving_avg_50=moving_avg_50,
            moving_avg_200=moving_avg_200,
            MACD=macd,
            analyst_rating=analyst_rating
        )

    def generate_random_stock_data(self) -> Tuple[Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators]:
        """
        Generate comprehensive random stock data with logical relationships.
        """
        # Generate stock basic information
        stock, market_cap = self._generate_stock_basic_info()

        # Generate current stock price
        # Stock price between $10 and $5000
        # This ensures the market_cap roughly aligns with shares_outstanding * price.
        # However, since both are random, it's approximate. That’s okay for initialization.
        current_price = round(random.uniform(10, 1200), 2)

        # Price and trading info
        price_info = self._generate_price_trading_info(
            stock.ticker, current_price)

        # Fundamentals with logical consistency
        fundamentals = self._generate_fundamental_metrics(
            stock.ticker, current_price, market_cap, stock.shares_outstanding)

        # Volatility and risk metrics depend on cap category
        risk_metrics = self._generate_volatility_risk(
            stock.ticker, stock.cap_category)

        # Market indicators remain randomized
        market_indicators = self._generate_market_indicators(
            stock.ticker, current_price)

        return stock, price_info, fundamentals, risk_metrics, market_indicators


def generate_random_stock_data() -> Tuple[Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators]:
    """
    Wrapper function to maintain original interface.
    """
    initializer = StockDataInitializer()
    return initializer.generate_random_stock_data()

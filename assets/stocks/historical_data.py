import random
import statistics
from datetime import datetime, timedelta
from collections import deque
from typing import List, Dict, Any


class StockDataGenerator:
    def __init__(self, ticker: str, start_price: float, shares_outstanding: int,
                 start_date: datetime, days: int,
                 initial_eps: float = 10.0,
                 annual_dividend: float = 5.0,
                 base_volume: int = 1_000_000):
        """
        Initialize stock data generation parameters
        """
        self.ticker = ticker
        self.start_price = start_price
        self.shares_outstanding = shares_outstanding
        self.start_date = start_date
        self.days = days
        self.initial_eps = initial_eps
        self.annual_dividend = annual_dividend
        self.base_volume = base_volume

        # Initialize tracking variables
        self.close_prices = deque(maxlen=200)
        self.close_prices.append(start_price)

        # Initial fundamental metrics
        self.eps = initial_eps
        self.dividend = annual_dividend
        self.roe = 10.0
        self.debt_to_equity = 0.5
        self.revenue_growth = 3.0
        self.net_income = self.eps * self.shares_outstanding
        self.pe_ratio = round(start_price / self.eps, 2)

        # Constants
        self.annual_growth_rate = 0.02  # 2% annual growth in equilibrium price
        self.daily_growth_factor = (1 + self.annual_growth_rate) ** (1 / 250)

    def _calculate_price_dynamics(self, prev_close: float, equilibrium_price: float) -> Dict[str, float]:
        """
        Calculate daily price dynamics using mean reversion
        """
        # Calculate deviation from equilibrium
        deviation = (prev_close - equilibrium_price) / equilibrium_price

        # Mean reversion: If price > equilibrium, expected return is negative
        # If price < equilibrium, expected return is positive
        daily_return = random.gauss(-0.001 * deviation, 0.01)

        close_price = prev_close * (1 + daily_return)
        open_price = close_price * random.uniform(0.995, 1.005)

        # Day high/low adjustments
        day_high = close_price * random.uniform(1.00, 1.02)
        day_low = close_price * random.uniform(0.98, 1.00)
        day_high = max(day_high, open_price, close_price)
        day_low = min(day_low, open_price, close_price)

        return {
            'close_price': close_price,
            'open_price': open_price,
            'day_high': day_high,
            'day_low': day_low,
            'daily_return': daily_return
        }

    def _calculate_volume(self, daily_return: float) -> int:
        """
        Simulate trading volume based on price volatility
        """
        volatility_factor = abs(daily_return) * 50_000
        trading_volume = int(
            self.base_volume +
            random.randint(-100_000, 100_000) +
            volatility_factor
        )
        return max(trading_volume, 100_000)

    def _calculate_rsi(self) -> int:
        """
        Calculate Relative Strength Index (RSI)
        """
        if len(self.close_prices) >= 15:
            gains, losses = [], []
            for i in range(1, 15):
                change = self.close_prices[-i] - self.close_prices[-(i+1)]
                (gains if change > 0 else losses).append(abs(change))

            avg_gain = sum(gains)/14 if gains else 0.0001
            avg_loss = sum(losses)/14 if losses else 0.0001
            rs = avg_gain / avg_loss
            return round(100 - (100/(1+rs)))
        return 50

    def _calculate_moving_averages(self) -> Dict[str, float]:
        """
        Calculate moving averages
        """
        ma_50 = round(statistics.mean(list(self.close_prices)[-50:]), 2) \
            if len(self.close_prices) >= 50 else \
            round(statistics.mean(self.close_prices), 2)

        ma_200 = round(statistics.mean(list(self.close_prices)), 2)

        return {
            'ma_50': ma_50,
            'ma_200': ma_200
        }

    def _calculate_macd(self) -> str:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        if len(self.close_prices) > 26:
            short_ma = statistics.mean(
                list(self.close_prices)[-12:]) \
                if len(self.close_prices) >= 12 else self.close_prices[-1]

            long_ma = statistics.mean(list(self.close_prices)[-26:])
            macd_value = short_ma - long_ma

            if macd_value > 0.5:
                return "Positive"
            elif macd_value < -0.5:
                return "Negative"

        return "Neutral"

    def _update_fundamentals(self, day: int) -> None:
        """
        Update fundamental metrics periodically
        """
        if day > 0 and day % 90 == 0:
            self.eps *= random.uniform(0.95, 1.05)
            self.net_income *= random.uniform(0.95, 1.05)

    def _determine_market_cap_category(self, market_cap: float) -> str:
        """
        Categorize market capitalization
        """
        if market_cap > 10**10:
            return "Large-Cap"
        elif market_cap > 2e9:
            return "Mid-Cap"
        return "Small-Cap"

    def generate_historical_data(self) -> List[Dict[str, Any]]:
        """
        Generate daily stock data
        """
        data = []
        prev_close = self.start_price
        current_date = self.start_date
        equilibrium_price = self.start_price

        for day in range(self.days):
            # Update equilibrium price
            equilibrium_price *= self.daily_growth_factor

            # Calculate price dynamics
            price_data = self._calculate_price_dynamics(
                prev_close, equilibrium_price)
            close_price = price_data['close_price']

            # Add to close prices for technical indicators
            self.close_prices.append(close_price)

            # Calculate market metrics
            market_cap = close_price * self.shares_outstanding
            pe_ratio = round(close_price / self.eps,
                             2) if self.eps > 0 else None
            dividend_yield = round((self.dividend / close_price) * 100, 2)

            # Calculate various indicators
            trading_volume = self._calculate_volume(price_data['daily_return'])
            rsi = self._calculate_rsi()
            moving_avgs = self._calculate_moving_averages()
            macd_signal = self._calculate_macd()

            # Periodic fundamental updates
            self._update_fundamentals(day)

            # Construct daily record
            daily_record = {
                "date": current_date.strftime("%Y-%m-%d"),
                "ticker": self.ticker,
                "company_name": "Placeholder Inc.",
                "sector": "Finance",
                "market_cap": round(market_cap, 2),
                "cap_category": self._determine_market_cap_category(market_cap),
                "shares_outstanding": self.shares_outstanding,

                "open_price": round(price_data['open_price'], 2),
                "close_price": round(close_price, 2),
                "day_high": round(price_data['day_high'], 2),
                "day_low": round(price_data['day_low'], 2),
                "week_52_high": None,
                "week_52_low": None,
                "trading_volume": trading_volume,
                "average_volume": None,

                "eps": round(self.eps, 2),
                "p_e_ratio": pe_ratio,
                "dividend_yield": dividend_yield,
                "roe": self.roe,
                "debt_to_equity": self.debt_to_equity,
                "revenue_growth": self.revenue_growth,
                "net_income": round(self.net_income, 2),

                "beta": 0.8,
                "standard_deviation": 8.0,
                "sharpe_ratio": 1.5,

                "RSI": rsi,
                "moving_avg_50": moving_avgs['ma_50'],
                "moving_avg_200": moving_avgs['ma_200'],
                "MACD": macd_signal,
                "analyst_rating": "Buy"
            }

            data.append(daily_record)
            prev_close = close_price
            current_date += timedelta(days=1)

        # Post-processing: calculate 52-week high/low and average volume
        self._add_extended_metrics(data)

        return data

    def _add_extended_metrics(self, data: List[Dict[str, Any]]) -> None:
        """
        Add 52-week high/low and average volume metrics
        """
        prices = [d['close_price'] for d in data]
        for i, d in enumerate(data):
            # 52-week (251 trading days) high/low
            window = prices[max(0, i-251):i+1]
            d['week_52_high'] = round(max(window), 2)
            d['week_52_low'] = round(min(window), 2)

            # 30-day average volume
            vols = [x['trading_volume'] for x in data[max(0, i-29):i+1]]
            d['average_volume'] = int(
                sum(vols) / len(vols)) if vols else d['trading_volume']


def generate_historical_data(
    ticker: str,
    start_price: float,
    shares_outstanding: int,
    start_date: datetime,
    days: int,
    initial_eps: float = 10.0,
    annual_dividend: float = 5.0,
    base_volume: int = 1_000_000
) -> List[Dict[str, Any]]:
    """
    Wrapper function to maintain original interface
    """
    generator = StockDataGenerator(
        ticker, start_price, shares_outstanding, start_date, days,
        initial_eps, annual_dividend, base_volume
    )
    return generator.generate_historical_data()

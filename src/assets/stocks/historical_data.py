# historical_Data.py
import random
import statistics
from datetime import datetime, timedelta
from collections import deque
from typing import List, Dict, Any
import math


class StockDataGenerator:
    def __init__(
        self,
        ticker: str,
        start_price: float,
        shares_outstanding: int,
        start_date: datetime,
        days: int,
        initial_eps: float = 10.0,
        annual_dividend: float = 5.0,
        base_volume: int = 1_000_000,
        initial_revenue_growth: float = 5.0,
        initial_roe: float = 15.0,
        initial_debt_to_equity: float = 0.5
    ):
        """
        Initialize parameters for stock data generation.
        We'll base drift and volatility on fundamentals and market cap.
        """
        self.ticker = ticker
        self.start_price = start_price
        self.shares_outstanding = shares_outstanding
        self.start_date = start_date
        self.days = days
        self.initial_eps = initial_eps
        self.annual_dividend = annual_dividend
        self.base_volume = base_volume
        self.revenue_growth = initial_revenue_growth  # In percentage
        self.roe = initial_roe
        self.debt_to_equity = initial_debt_to_equity

        # Initialize fundamentals
        self.eps = initial_eps
        self.net_income = self.eps * self.shares_outstanding
        self.pe_ratio = round(self.start_price / self.eps, 2)

        # A placeholder sector - could be parameterized
        self.sector = "Finance"

        # Tracking prices for indicators
        self.close_prices = deque(maxlen=300)
        self.close_prices.append(start_price)

        # Determine initial market cap and category
        self.market_cap = start_price * shares_outstanding
        self.cap_category = self._determine_market_cap_category(
            self.market_cap)

        # Determine annual drift (mu) and annual volatility (sigma) based on fundamentals
        # Logic: higher growth + moderate PE => positive drift; large cap => less volatile
        # This is arbitrary logic for demonstration only.
        self.annual_drift = self._calculate_annual_drift()
        self.annual_volatility = self._calculate_annual_volatility()

        # Convert annual parameters to daily
        self.daily_mu = self.annual_drift / 252
        self.daily_sigma = self.annual_volatility / (252**0.5)
        self.daily_sigma = min(self.daily_sigma, 0.1)  # Cap volatility at 10%

    def _calculate_annual_drift(self) -> float:
        """
        Calculate annual drift (mu_annual) based on fundamentals:
        - Start with a base drift around the revenue growth.
        - Adjust slightly by P/E ratio (if P/E too high, lower drift).
        - Adjust by market cap category (smaller cap = higher expected growth).
        """
        base = (self.revenue_growth / 100.0)  # revenue_growth% as decimal
        # If P/E > 20, consider it slightly overvalued and reduce drift
        pe_adjust = -0.0005 * \
            (self.pe_ratio - 20) if self.pe_ratio > 20 else 0.0005 * \
            (20 - self.pe_ratio)
        # Cap category effect: Smaller caps have slightly higher expected growth
        if self.cap_category == "Small-Cap":
            cap_adjust = 0.02
        elif self.cap_category == "Mid-Cap":
            cap_adjust = 0.01
        else:
            cap_adjust = 0.0

        # Combine them
        mu_annual = base + pe_adjust + cap_adjust
        # Ensure it's within a reasonable range
        # between -5% and 20% per year
        mu_annual = max(-0.05, min(mu_annual, 0.2))
        return mu_annual

    def _calculate_annual_volatility(self) -> float:
        """
        Estimate annual volatility:
        - Base volatility is sector and cap based.
        For simplicity, let's assume:
        - Small-Cap: 30% to 50% annual vol
        - Mid-Cap: 20% to 35%
        - Large-Cap: 10% to 25%
        """
        if self.cap_category == "Large-Cap":
            vol = random.uniform(0.10, 0.25)
        elif self.cap_category == "Mid-Cap":
            vol = random.uniform(0.20, 0.35)
        else:
            vol = random.uniform(0.30, 0.50)
        return vol

    def _determine_market_cap_category(self, market_cap: float) -> str:
        """
        Categorize market capitalization
        """
        if market_cap > 10**10:
            return "Large-Cap"
        elif market_cap > 2e9:
            return "Mid-Cap"
        return "Small-Cap"

    def _simulate_price(self, prev_close: float) -> float:
        """
        Simulate next day's price using GBM
        S_{t+1} = S_t * exp((mu - sigma^2/2)*dt + sigma*sqrt(dt)*Z)
        dt = 1/252 for daily
        """
        dt = 1/252
        z = random.gauss(0, 1)
        drift_term = (self.daily_mu - 0.5 * self.daily_sigma**2) * dt
        diffusion_term = self.daily_sigma * math.sqrt(dt) * z
        next_price = prev_close * math.exp(drift_term + diffusion_term)
        return next_price

    def _calculate_intraday_range(self, open_price: float, close_price: float) -> Dict[str, float]:
        """
        Calculate tentative day_high and day_low using a volatility-based approach.
        The idea is to use daily_sigma to determine how much variation we can see in a day.
        
        A normal approach:
        - Compute a random factor for the day's range based on daily_sigma.
        - day_high is slightly above the max(open, close)
        - day_low is slightly below the min(open, close)
        """
        # For demonstration, let's draw a random number from a normal distribution centered at 0
        # and scale it by daily_sigma. This represents intraday volatility.
        # smaller factor for intraday
        z = random.gauss(0, self.daily_sigma / 2)
        high_anchor = max(open_price, close_price)
        low_anchor = min(open_price, close_price)

        # day_high and day_low vary around these anchors
        # Example: If z is positive, day_high stretches more above the anchor.
        # If z is negative, day_low extends lower.
        # We'll ensure logical ordering later, so exact logic is flexible.
        day_high = high_anchor * (1 + abs(z))
        day_low = low_anchor * (1 - abs(z))

        return {
            'day_high': day_high,
            'day_low': day_low
        }

    def _ensure_logical_ordering(self, open_price: float, close_price: float, day_high: float, day_low: float) -> Dict[str, float]:
        """
        Ensure that:
        - day_high >= open_price and day_high >= close_price
        - day_low <= open_price and day_low <= close_price
        
        If not, adjust them accordingly.
        """
        # Ensure day_high is not less than either the open or close
        day_high = max(day_high, open_price, close_price)
        # Ensure day_low is not greater than either the open or close
        day_low = min(day_low, open_price, close_price)

        return {
            'day_high': day_high,
            'day_low': day_low
        }

    def _limit_intraday_range(self, close_price: float, day_high: float, day_low: float, max_intraday_percentage: float = 0.03) -> Dict[str, float]:
        """
            Limit the intraday price range to a maximum percentage of the close price.
            For example, if max_intraday_percentage = 0.03 (3%), the range (day_high - day_low)
            should not exceed 3% of close_price.

            If it does, compress the range around the midpoint.
        """
        allowed_range = max_intraday_percentage * close_price
        current_range = day_high - day_low

        if current_range > allowed_range:
            midpoint = (day_high + day_low) / 2
            day_high = midpoint + allowed_range / 2
            day_low = midpoint - allowed_range / 2

        return {
            'day_high': day_high,
            'day_low': day_low
        }

    def _calculate_daily_prices(self, close_price: float) -> Dict[str, float]:
        """
        Given today's close price, determine open, high, low using logical constraints:
        1. Determine open price as close +/- a small random percent.
        2. Use intraday range logic based on volatility to get preliminary day_high, day_low.
        3. Ensure logical ordering.
        4. Limit the intraday range if it exceeds a certain percentage.
        """
        # Step 1: Open price slightly around close price
        open_price = close_price * random.uniform(0.995, 1.005)

        # Step 2: Get preliminary day_high, day_low from volatility logic
        intraday = self._calculate_intraday_range(open_price, close_price)
        day_high = intraday['day_high']
        day_low = intraday['day_low']

        # Step 3: Ensure logical ordering
        ordered = self._ensure_logical_ordering(
            open_price, close_price, day_high, day_low)
        day_high = ordered['day_high']
        day_low = ordered['day_low']

        # Step 4: Limit the intraday range if it's too large
        limited = self._limit_intraday_range(
            close_price, day_high, day_low, max_intraday_percentage=0.03+self.daily_sigma)
        day_high = limited['day_high']
        day_low = limited['day_low']

        return {
            'open_price': round(open_price, 2),
            'day_high': round(day_high, 2),
            'day_low': round(day_low, 2)
        }

    def _calculate_volume(self, daily_return: float) -> int:
        """
        Simulate trading volume based on price volatility and daily return.
        Higher absolute returns => higher volume.
        Use base_volume and add a factor of daily_return and random variation.
        """
        volatility_factor = abs(daily_return) * self.base_volume
        random_factor = random.randint(-int(self.base_volume*0.1),
                                       int(self.base_volume*0.1))
        trading_volume = int(self.base_volume +
                             volatility_factor + random_factor)
        return max(trading_volume, 100_000)

    def _calculate_rsi(self) -> int:
        """
        Calculate Relative Strength Index (RSI)
        Based on last 14 periods of close prices
        """
        if len(self.close_prices) >= 15:
            gains, losses = [], []
            prices = list(self.close_prices)
            for i in range(1, 15):
                change = prices[-i] - prices[-(i+1)]
                (gains if change > 0 else losses).append(abs(change))

            avg_gain = sum(gains)/14 if gains else 0.0001
            avg_loss = sum(losses)/14 if losses else 0.0001
            rs = avg_gain / avg_loss
            return round(100 - (100/(1+rs)))
        return 50

    def _calculate_moving_averages(self) -> Dict[str, float]:
        """
        Calculate moving averages (50-day and 200-day)
        """
        prices = list(self.close_prices)
        ma_50 = round(statistics.mean(prices[-50:]), 2) if len(
            self.close_prices) >= 50 else round(statistics.mean(prices), 2)
        ma_200 = round(statistics.mean(prices[-200:]), 2) if len(
            self.close_prices) >= 200 else round(statistics.mean(prices), 2)
        return {
            'ma_50': ma_50,
            'ma_200': ma_200
        }

    def _calculate_macd(self) -> str:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Using 12-day and 26-day EMA approximations here just by mean for simplicity
        """
        prices = list(self.close_prices)
        if len(prices) > 26:
            short_ma = statistics.mean(
                prices[-12:]) if len(prices) >= 12 else prices[-1]
            long_ma = statistics.mean(prices[-26:])
            macd_value = short_ma - long_ma

            if macd_value > 0.5:
                return "Positive"
            elif macd_value < -0.5:
                return "Negative"

        return "Neutral"

    def _update_fundamentals(self, day: int) -> None:
        """
        Every quarter (90 days), update EPS, net income, and revenue growth slightly.
        This simulates the release of new earnings reports.
        """
        if day > 0 and day % 90 == 0:
            # EPS and net income fluctuate within +/-5%
            self.eps *= random.uniform(0.95, 1.05)
            self.net_income = self.eps * self.shares_outstanding
            # Revenue growth might change slightly too
            self.revenue_growth *= random.uniform(0.95, 1.05)

            # Adjust ROE and debt-to-equity slightly as well
            self.roe *= random.uniform(0.95, 1.05)
            self.debt_to_equity *= random.uniform(0.95, 1.05)

            # Recalculate P/E after EPS shift (price will reflect new info going forward)
            # (No immediate price jump here, but drift will reflect fundamentals over time)
            if self.eps > 0:
                current_price = self.close_prices[-1]
                self.pe_ratio = round(current_price / self.eps, 2)
            else:
                self.pe_ratio = None

    def generate_historical_data(self) -> List[Dict[str, Any]]:
        """
        Generate daily stock data using GBM for price and logical updates for fundamentals.
        """
        data = []
        prev_close = self.start_price
        current_date = self.start_date

        for day in range(self.days):
            # Simulate price
            close_price = self._simulate_price(prev_close)
            self.close_prices.append(close_price)

            daily_return = (close_price - prev_close) / prev_close

            # Calculate daily prices
            price_data = self._calculate_daily_prices(close_price)

            # Market metrics
            market_cap = close_price * self.shares_outstanding
            pe_ratio = round(close_price / self.eps,
                             2) if self.eps > 0 else None
            dividend_yield = round(
                (self.annual_dividend / close_price) * 100, 2)

            # Indicators
            trading_volume = self._calculate_volume(daily_return)
            rsi = self._calculate_rsi()
            moving_avgs = self._calculate_moving_averages()
            macd_signal = self._calculate_macd()

            # Update fundamentals periodically
            self._update_fundamentals(day)

            daily_record = {
                "date": current_date.strftime("%Y-%m-%d"),
                "ticker": self.ticker,
                "company_name": "Placeholder Inc.",
                "sector": self.sector,
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
                "roe": round(self.roe, 2),
                "debt_to_equity": round(self.debt_to_equity, 2),
                "revenue_growth": round(self.revenue_growth, 2),
                "net_income": round(self.net_income, 2),

                # Risk metrics could also evolve over time, but we keep it simple
                "beta": round(random.uniform(0.7, 1.3), 2),
                # daily sigma as %
                "standard_deviation": round(self.daily_sigma * 100, 2),
                "sharpe_ratio": round((self.daily_mu / self.daily_sigma) * (252**0.5), 2),

                "RSI": rsi,
                "moving_avg_50": moving_avgs['ma_50'],
                "moving_avg_200": moving_avgs['ma_200'],
                "MACD": macd_signal,
                "analyst_rating": random.choice(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])
            }

            data.append(daily_record)
            prev_close = close_price
            current_date += timedelta(days=1)

        # Post-processing: 52-week high/low and average volume
        self._add_extended_metrics(data)

        return data

    def _add_extended_metrics(self, data: List[Dict[str, Any]]) -> None:
        """
        Add 52-week high/low and average volume metrics after all data is generated.
        """
        prices = [d['close_price'] for d in data]
        for i, d in enumerate(data):
            # 52-week window is approx 252 trading days
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
    Wrapper function to maintain original interface.
    """
    generator = StockDataGenerator(
        ticker, start_price, shares_outstanding, start_date, days,
        initial_eps, annual_dividend, base_volume
    )
    return generator.generate_historical_data()

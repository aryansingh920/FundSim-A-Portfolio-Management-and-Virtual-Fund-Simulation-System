"""
Created on 29/12/2024

@author: Aryan

Filename: historical_data.py

Relative Path: src/assets/stocks/historical_data.py
"""

import random
import statistics
import math

from datetime import datetime, timedelta
from collections import deque
from typing import List, Dict, Any

# NEW: Import Session if you plan to bulk-insert intraday data
from sqlalchemy.orm import Session

from assets.stocks.model import IntradayData


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
        self.annual_drift = self._calculate_annual_drift()
        self.annual_volatility = self._calculate_annual_volatility()

        # Convert annual parameters to daily
        self.daily_mu = self.annual_drift / 252
        self.daily_sigma = self.annual_volatility / (252 ** 0.5)
        # Cap daily volatility at 10%
        self.daily_sigma = min(self.daily_sigma, 0.1)

    def _determine_market_cap_category(self, market_cap: float) -> str:
        """
        Categorize market capitalization
        """
        if market_cap > 10**10:
            return "Large-Cap"
        elif market_cap > 2e9:
            return "Mid-Cap"
        return "Small-Cap"

    def _calculate_annual_drift(self) -> float:
        """
        Calculate annual drift (mu_annual) based on fundamentals:
        - Start with a base drift around the revenue growth.
        - Adjust slightly by P/E ratio (if P/E > 20, reduce drift).
        - Adjust by market cap category (smaller cap => higher expected growth).
        """
        base = self.revenue_growth / 100.0  # e.g. 5% => 0.05

        if self.pe_ratio > 20:
            pe_adjust = -0.0005 * (self.pe_ratio - 20)
        else:
            pe_adjust = 0.0005 * (20 - self.pe_ratio)

        if self.cap_category == "Small-Cap":
            cap_adjust = 0.02
        elif self.cap_category == "Mid-Cap":
            cap_adjust = 0.01
        else:
            cap_adjust = 0.0

        mu_annual = base + pe_adjust + cap_adjust
        return max(-0.05, min(mu_annual, 0.2))

    def _calculate_annual_volatility(self) -> float:
        """
        Estimate annual volatility ranges:
            Small-Cap:  30% - 50%
            Mid-Cap:    20% - 35%
            Large-Cap:  10% - 25%
        """
        if self.cap_category == "Large-Cap":
            return random.uniform(0.10, 0.25)
        elif self.cap_category == "Mid-Cap":
            return random.uniform(0.20, 0.35)
        else:
            return random.uniform(0.30, 0.50)

    def _simulate_price(self, prev_close: float) -> float:
        """
        Simulate next day's price using GBM: 
        S_{t+1} = S_t * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        """
        dt = 1 / 252
        z = random.gauss(0, 1)
        drift_term = (self.daily_mu - 0.5 * self.daily_sigma**2) * dt
        diffusion_term = self.daily_sigma * math.sqrt(dt) * z
        return prev_close * math.exp(drift_term + diffusion_term)

    # -------------------
    # Intraday Data Logic
    # -------------------
    def generate_intraday_data(
        self,
        ticker: str,
        trade_date: datetime.date,
        open_price: float,
        close_price: float,
        day_high: float,
        day_low: float,
        market_open: datetime,
        market_close: datetime,
        frequency_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate intraday (e.g. every 5 seconds) price points for a single day.
        Returns a list of records ready for DB insertion.
        """
        records = []
        total_seconds = int((market_close - market_open).total_seconds())

        # Linear interpolation from open->close as baseline; then add random noise.
        price_slope = (close_price - open_price) / total_seconds

        current_time = market_open
        while current_time < market_close:
            elapsed = (current_time - market_open).total_seconds()
            base_line_price = open_price + price_slope * elapsed

            # Add random noise ±1% of the opening price
            noise_range = 0.01 * open_price
            noise = random.uniform(-noise_range, noise_range)

            sim_price = base_line_price + noise
            sim_price = min(sim_price, day_high)
            sim_price = max(sim_price, day_low)

            # Simple random volume
            sim_volume = random.randint(50, 2000)

            records.append({
                "ticker": ticker,
                "date": trade_date,
                "timestamp": current_time,
                "price": round(sim_price, 2),
                "volume": sim_volume,
            })

            current_time += timedelta(seconds=frequency_seconds)

        return records

    def store_intraday_data(self, session: Session, intraday_records: List[Dict[str, Any]]):
        """
        Bulk insert intraday data into intraday_data table.
        """
        to_insert = []
        for r in intraday_records:
            obj = IntradayData(
                ticker=r["ticker"],
                date=r["date"],
                timestamp=r["timestamp"],
                price=r["price"],
                volume=r["volume"],
            )
            to_insert.append(obj)

        session.bulk_save_objects(to_insert)
        session.commit()

    # -------------------
    # Daily Data Logic
    # -------------------
    def _calculate_daily_prices(self, close_price: float) -> Dict[str, float]:
        """
        Generate open/day_high/day_low for today's daily record.
        """
        # Step 1: open ~ close ± (0.5%)
        open_price = close_price * random.uniform(0.995, 1.005)

        # Step 2: figure out day_high/day_low using intraday-like logic
        intraday = self._calculate_intraday_range(open_price, close_price)
        day_high, day_low = intraday["day_high"], intraday["day_low"]

        # Step 3: ensure ordering
        ordered = self._ensure_logical_ordering(
            open_price, close_price, day_high, day_low)
        day_high, day_low = ordered["day_high"], ordered["day_low"]

        # Step 4: limit range if it’s abnormally large
        limited = self._limit_intraday_range(
            close_price, day_high, day_low, 0.03 + self.daily_sigma)
        day_high, day_low = limited["day_high"], limited["day_low"]

        return {
            "open_price": round(open_price, 2),
            "day_high": round(day_high, 2),
            "day_low": round(day_low, 2),
        }

    def _calculate_intraday_range(self, open_price: float, close_price: float) -> Dict[str, float]:
        """
        Simple approach: day_high/day_low based on daily_sigma.
        """
        z = random.gauss(0, self.daily_sigma / 2)
        high_anchor = max(open_price, close_price)
        low_anchor = min(open_price, close_price)

        day_high = high_anchor * (1 + abs(z))
        day_low = low_anchor * (1 - abs(z))

        return {"day_high": day_high, "day_low": day_low}

    def _ensure_logical_ordering(
        self, open_price: float, close_price: float, day_high: float, day_low: float
    ) -> Dict[str, float]:
        """
        Guarantee day_high >= open, day_high >= close and day_low <= open, day_low <= close
        """
        day_high = max(day_high, open_price, close_price)
        day_low = min(day_low, open_price, close_price)
        return {"day_high": day_high, "day_low": day_low}

    def _limit_intraday_range(
        self, close_price: float, day_high: float, day_low: float, max_intraday_percentage: float
    ) -> Dict[str, float]:
        """
        Clamp day_high-day_low to not exceed a certain fraction of close_price.
        """
        allowed_range = close_price * max_intraday_percentage
        current_range = day_high - day_low
        if current_range > allowed_range:
            midpoint = (day_high + day_low) / 2
            day_high = midpoint + allowed_range / 2
            day_low = midpoint - allowed_range / 2

        return {"day_high": day_high, "day_low": day_low}

    def _calculate_volume(self, daily_return: float) -> int:
        """
        Simulate daily trading volume based on absolute return + random fluctuation.
        """
        volatility_factor = abs(daily_return) * self.base_volume
        random_factor = random.randint(
            -int(self.base_volume * 0.1),
            int(self.base_volume * 0.1)
        )
        volume = int(self.base_volume + volatility_factor + random_factor)
        return max(volume, 100_000)

    def _calculate_rsi(self) -> int:
        """
        Approximate RSI from last 14 close prices.
        """
        if len(self.close_prices) >= 15:
            gains, losses = [], []
            prices = list(self.close_prices)
            for i in range(1, 15):
                diff = prices[-i] - prices[-(i + 1)]
                (gains if diff > 0 else losses).append(abs(diff))

            avg_gain = sum(gains) / 14 if gains else 0.0001
            avg_loss = sum(losses) / 14 if losses else 0.0001
            rs = avg_gain / avg_loss
            return round(100 - (100 / (1 + rs)))
        return 50

    def _calculate_moving_averages(self) -> Dict[str, float]:
        """
        Simple 50-day and 200-day MAs from self.close_prices
        """
        prices = list(self.close_prices)

        if len(prices) >= 50:
            ma_50 = round(statistics.mean(prices[-50:]), 2)
        else:
            ma_50 = round(statistics.mean(prices), 2)

        if len(prices) >= 200:
            ma_200 = round(statistics.mean(prices[-200:]), 2)
        else:
            ma_200 = round(statistics.mean(prices), 2)

        return {"ma_50": ma_50, "ma_200": ma_200}

    def _calculate_macd(self) -> str:
        """
        Fake MACD: short MA (12) - long MA (26)
        """
        prices = list(self.close_prices)
        if len(prices) > 26:
            short_ma = statistics.mean(
                prices[-12:]) if len(prices) >= 12 else prices[-1]
            long_ma = statistics.mean(prices[-26:])
            macd_val = short_ma - long_ma
            if macd_val > 0.5:
                return "Positive"
            elif macd_val < -0.5:
                return "Negative"
        return "Neutral"

    def _update_fundamentals(self, day: int) -> None:
        """
        Every 90 days, slightly adjust EPS/net_income/revenue_growth, etc.
        """
        if day > 0 and (day % 90 == 0):
            self.eps *= random.uniform(0.95, 1.05)
            self.net_income = self.eps * self.shares_outstanding
            self.revenue_growth *= random.uniform(0.95, 1.05)
            self.roe *= random.uniform(0.95, 1.05)
            self.debt_to_equity *= random.uniform(0.95, 1.05)

            if self.eps > 0:
                current_price = self.close_prices[-1]
                self.pe_ratio = round(current_price / self.eps, 2)
            else:
                self.pe_ratio = None

    def generate_historical_data(self) -> List[Dict[str, Any]]:
        """
        Generate daily historical data using GBM for price movement.
        """
        data = []
        prev_close = self.start_price
        current_date = self.start_date

        for day in range(self.days):
            # 1) price sim
            close_price = self._simulate_price(prev_close)
            self.close_prices.append(close_price)

            daily_return = (close_price - prev_close) / prev_close

            # 2) open/high/low
            price_info = self._calculate_daily_prices(close_price)

            # 3) basic metrics
            market_cap = close_price * self.shares_outstanding
            pe_ratio = round(close_price / self.eps,
                             2) if self.eps > 0 else None
            dividend_yield = round(
                (self.annual_dividend / close_price) * 100, 2)

            # 4) indicators
            vol = self._calculate_volume(daily_return)
            rsi = self._calculate_rsi()
            ma = self._calculate_moving_averages()
            macd = self._calculate_macd()

            # 5) fundamentals update (quarterly)
            self._update_fundamentals(day)

            record = {
                "date": current_date.strftime("%Y-%m-%d"),
                "ticker": self.ticker,
                "company_name": "Placeholder Inc.",
                "sector": self.sector,
                "market_cap": round(market_cap, 2),
                "cap_category": self._determine_market_cap_category(market_cap),
                "shares_outstanding": self.shares_outstanding,

                "open_price": round(price_info["open_price"], 2),
                "close_price": round(close_price, 2),
                "day_high": round(price_info["day_high"], 2),
                "day_low": round(price_info["day_low"], 2),
                "week_52_high": None,
                "week_52_low": None,
                "trading_volume": vol,
                "average_volume": None,

                "eps": round(self.eps, 2),
                "p_e_ratio": pe_ratio,
                "dividend_yield": dividend_yield,
                "roe": round(self.roe, 2),
                "debt_to_equity": round(self.debt_to_equity, 2),
                "revenue_growth": round(self.revenue_growth, 2),
                "net_income": round(self.net_income, 2),

                # risk
                "beta": round(random.uniform(0.7, 1.3), 2),
                "standard_deviation": round(self.daily_sigma * 100, 2),
                "sharpe_ratio": round((self.daily_mu / self.daily_sigma) * (252**0.5), 2),

                # indicators
                "RSI": rsi,
                "moving_avg_50": ma["ma_50"],
                "moving_avg_200": ma["ma_200"],
                "MACD": macd,
                "analyst_rating": random.choice(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])
            }

            data.append(record)
            prev_close = close_price
            current_date += timedelta(days=1)

        self._add_extended_metrics(data)
        return data

    def _add_extended_metrics(self, data: List[Dict[str, Any]]) -> None:
        """
        After data is generated, compute 52-week high/low + 30-day average volume.
        """
        # For 52-week, we just consider up to 252 days in the past
        closes = [day["close_price"] for day in data]

        for i, day_dict in enumerate(data):
            window = closes[max(0, i - 251):i + 1]
            day_dict["week_52_high"] = round(max(window), 2)
            day_dict["week_52_low"] = round(min(window), 2)

            # 30-day average volume
            volumes_window = [d["trading_volume"]
                              for d in data[max(0, i - 29):i + 1]]
            if volumes_window:
                day_dict["average_volume"] = int(
                    sum(volumes_window) / len(volumes_window))
            else:
                day_dict["average_volume"] = day_dict["trading_volume"]


# ------------
# Wrapper
# ------------
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
    Wrapper function to maintain the original interface.
    Generates daily historical data for `days` using StockDataGenerator.
    """
    generator = StockDataGenerator(
        ticker,
        start_price,
        shares_outstanding,
        start_date,
        days,
        initial_eps,
        annual_dividend,
        base_volume
    )
    return generator.generate_historical_data()

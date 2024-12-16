# initialization.py
import random
from faker import Faker
import numpy as np
from model.model import (
    Stock,
    PriceTradingInfo,
    FundamentalMetrics,
    VolatilityRisk,
    MarketIndicators
)
from constants import SECTORS

def cap_category(market_cap):
    if market_cap > 10**10:
        cap_category = "Large-Cap"
    elif market_cap > 2 * 10**9:
        cap_category = "Mid-Cap"
    else:
        cap_category = "Small-Cap"
    return cap_category


used_tickers = set()

import random
import string

# Set to keep track of generated tickers
generated_tickers = set()

def generate_unique_ticker():
    while True:
        # Generate a random length between 3 and 5
        length = random.randint(3, 5)
        # Generate a random ticker of the given length
        ticker = ''.join(random.choices(string.ascii_uppercase, k=length))
        # Check if the ticker is unique
        if ticker not in generated_tickers:
            generated_tickers.add(ticker)
            return ticker

def generate_market_cap():
    # Weighted random choice for better distribution
    cap_category = random.choices(
        ["Small-Cap", "Mid-Cap", "Large-Cap"],
        weights=[0.4, 0.4, 0.2],  # 40% Small, 40% Mid, 20% Large
        k=1
    )[0]

    if cap_category == "Small-Cap":
        return random.uniform(1e8, 2e9)  # $100M to $2B
    elif cap_category == "Mid-Cap":
        return random.uniform(2e9, 10e9)  # $2B to $10B
    else:  # Large-Cap
        return random.uniform(10e9, 2e12)  # $10B to $2T


# Function to generate random stock data
def generate_random_stock_data():
    fake = Faker()
    
    # Randomized Basic Stock Information
    ticker = generate_unique_ticker()
    company_name = fake.company()
    sector = random.choice(SECTORS)
    market_cap = market_cap = generate_market_cap()
    shares_outstanding = random.randint(10**6, 10**10)  # Between 1M to 10B shares

    # cap_category = cap_category(market_cap)

    # Initialize Stock Object
    stock = Stock(
        ticker=ticker,
        company_name=company_name,
        sector=sector,
        market_cap=round(market_cap, 2),
        cap_category=cap_category(market_cap),
        shares_outstanding=shares_outstanding
    )

    # Randomized Price and Trading Information
    current_price = round(random.uniform(10, 5000), 2)  # Stock price between $10 and $5000
    open_price = round(current_price * random.uniform(0.98, 1.02), 2)
    close_price = current_price
    day_high = round(current_price * random.uniform(1.01, 1.05), 2)
    day_low = round(current_price * random.uniform(0.95, 0.99), 2)
    week_52_high = round(current_price * random.uniform(1.2, 1.5), 2)
    week_52_low = round(current_price * random.uniform(0.5, 0.8), 2)
    trading_volume = random.randint(10**5, 10**7)  # Between 100K to 10M shares
    average_volume = int(trading_volume * random.uniform(0.8, 1.2))

    price_info = PriceTradingInfo(
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

    # Randomized Fundamental Metrics
    eps = round(random.uniform(0.5, 15), 2)  # Earnings per share
    price_to_earnings = round(current_price / eps, 2)
    dividend_yield = round(random.uniform(0, 5), 2)
    roe = round(random.uniform(5, 30), 2)
    debt_to_equity = round(random.uniform(0.1, 2.5), 2)
    revenue_growth = round(random.uniform(1, 15), 2)
    net_income = round(market_cap * random.uniform(0.01, 0.1), 2)

    fundamentals = FundamentalMetrics(
        ticker=ticker,
        earnings_per_share=eps,
        price_to_earnings=price_to_earnings,
        dividend_yield=dividend_yield,
        return_on_equity=roe,
        debt_to_equity=debt_to_equity,
        revenue_growth=revenue_growth,
        net_income=net_income
    )

    # Randomized Volatility and Risk Metrics
    beta = round(random.uniform(0.5, 2.0), 2)
    standard_deviation = round(random.uniform(5, 30), 2)  # Percentage
    sharpe_ratio = round(random.uniform(-1, 3), 2)

    risk_metrics = VolatilityRisk(
        ticker=ticker,
        beta=beta,
        standard_deviation=standard_deviation,
        sharpe_ratio=sharpe_ratio
    )

    # Randomized Market Sentiment and Indicators
    rsi = random.randint(10, 90)
    moving_avg_50 = round(current_price * random.uniform(0.9, 1.1), 2)
    moving_avg_200 = round(current_price * random.uniform(0.8, 1.2), 2)
    macd = random.choice(["Positive", "Negative", "Neutral"])
    analyst_rating = random.choice(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])

    market_indicators = MarketIndicators(
        ticker=ticker,
        RSI=rsi,
        moving_avg_50=moving_avg_50,
        moving_avg_200=moving_avg_200,
        MACD=macd,
        analyst_rating=analyst_rating
    )

    return stock, price_info, fundamentals, risk_metrics, market_indicators



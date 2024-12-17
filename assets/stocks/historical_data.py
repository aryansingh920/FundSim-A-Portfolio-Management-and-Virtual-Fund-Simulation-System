# historical_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.model import Base, Stock, HistoricalData, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators
from datetime import datetime, timedelta
from collections import deque
import random
import statistics


def generate_historical_data(
    ticker: str,
    start_price: float,
    shares_outstanding: int,
    start_date: datetime,
    days: int,
    initial_eps: float = 10.0,
    annual_dividend: float = 5.0,
    base_volume: int = 1_000_000
):
    """
    Generate `days` of daily stock data for a given ticker with logical relationships.
    """

    data = []
    close_prices = deque(maxlen=200)
    close_prices.append(start_price)

    # Fundamental assumptions
    eps = initial_eps
    dividend = annual_dividend
    roe = 10.0
    debt_to_equity = 0.5
    revenue_growth = 3.0
    net_income = eps * shares_outstanding
    pe_ratio = round(start_price / eps, 2)

    analyst_rating = "Buy"
    macd_signal = "Neutral"

    equilibrium_price = start_price
    annual_growth_rate = 0.02  # 2% annual growth in equilibrium price
    daily_growth_factor = (1 + annual_growth_rate) ** (1 /
                                                       250)  # ~250 trading days in a year

    prev_close = start_price
    current_date = start_date

    for day in range(days):

        # Update equilibrium price slightly each day to reflect fundamental growth
        equilibrium_price *= daily_growth_factor

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

        market_cap = close_price * shares_outstanding
        pe_ratio = round(close_price / eps, 2) if eps > 0 else None
        dividend_yield = round((dividend / close_price) * 100, 2)

        # Volume simulation
        volatility_factor = abs(daily_return) * 50_000
        trading_volume = int(
            base_volume + random.randint(-100_000, 100_000) + volatility_factor)
        trading_volume = max(trading_volume, 100_000)

        close_prices.append(close_price)

        # RSI Calculation (simplified)
        if len(close_prices) >= 15:
            gains, losses = [], []
            for i in range(1, 15):
                change = close_prices[-i] - close_prices[-(i+1)]
                (gains if change > 0 else losses).append(abs(change))
            avg_gain = sum(gains)/14 if gains else 0.0001
            avg_loss = sum(losses)/14 if losses else 0.0001
            rs = avg_gain / avg_loss
            rsi = round(100 - (100/(1+rs)))
        else:
            rsi = 50

        # Moving Averages
        ma_50 = round(statistics.mean(list(close_prices)[-50:]), 2) if len(
            close_prices) >= 50 else round(statistics.mean(close_prices), 2)
        ma_200 = round(statistics.mean(list(close_prices)), 2)

        # MACD (simplified)
        if len(close_prices) > 26:
            short_ma = statistics.mean(
                list(close_prices)[-12:]) if len(close_prices) >= 12 else close_price
            long_ma = statistics.mean(list(close_prices)[-26:])
            macd_value = short_ma - long_ma
            if macd_value > 0.5:
                macd_signal = "Positive"
            elif macd_value < -0.5:
                macd_signal = "Negative"
            else:
                macd_signal = "Neutral"
        else:
            macd_signal = "Neutral"

        # Update fundamentals every 90 days
        if day > 0 and day % 90 == 0:
            eps *= random.uniform(0.95, 1.05)
            net_income *= random.uniform(0.95, 1.05)

        beta = 0.8
        standard_deviation = 8.0
        sharpe_ratio = 1.5

        final_cap_category = ""
        if market_cap > 10**10:
            final_cap_category = "Large-Cap"

        elif market_cap > 2e9:
            final_cap_category = "Mid-Cap"
        else:
            final_cap_category = "Small-Cap"

        daily_record = {
            "date": current_date.strftime("%Y-%m-%d"),
            "ticker": ticker,
            "company_name": "Placeholder Inc.",
            "sector": "Finance",
            "market_cap": round(market_cap, 2),
            "cap_category": final_cap_category,
            "shares_outstanding": shares_outstanding,

            "open_price": round(open_price, 2),
            "close_price": round(close_price, 2),
            "day_high": round(day_high, 2),
            "day_low": round(day_low, 2),
            "week_52_high": None,
            "week_52_low": None,
            "trading_volume": trading_volume,
            "average_volume": None,

            "eps": round(eps, 2),
            "p_e_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "roe": roe,
            "debt_to_equity": debt_to_equity,
            "revenue_growth": revenue_growth,
            "net_income": round(net_income, 2),

            "beta": beta,
            "standard_deviation": standard_deviation,
            "sharpe_ratio": sharpe_ratio,

            "RSI": rsi,
            "moving_avg_50": ma_50,
            "moving_avg_200": ma_200,
            "MACD": macd_signal,
            "analyst_rating": analyst_rating
        }

        data.append(daily_record)
        prev_close = close_price
        current_date += timedelta(days=1)

    # Compute 52-week high/low and average volume
    prices = [d['close_price'] for d in data]
    for i, d in enumerate(data):
        window = prices[max(0, i-251):i+1]
        d['week_52_high'] = round(max(window), 2)
        d['week_52_low'] = round(min(window), 2)

        vols = [x['trading_volume'] for x in data[max(0, i-29):i+1]]
        d['average_volume'] = int(
            sum(vols) / len(vols)) if vols else d['trading_volume']

    return data


# if __name__ == "__main__":
#     # Example parameters – in a real scenario, these might be passed as arguments or user input.
#     ticker = "AAPL"
#     start_price = 3000.0
#     shares_outstanding = 8_000_000_000
#     start_date = datetime(2020, 1, 1)
#     days = 365
#     initial_eps = 10.0
#     annual_dividend = 5.0
#     base_volume = 1_000_000

#     # Connect to DB and create tables if needed
#     engine = create_engine('sqlite:///data/stocks.db', echo=True)
#     Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # Check if stock exists, if not create it
#     stock = session.query(Stock).filter_by(ticker=ticker).first()
#     if not stock:
#         stock = Stock(
#             ticker=ticker,
#             company_name="Placeholder Inc.",
#             sector="Finance",
#             market_cap=0.0,
#             cap_category="Mid-Cap",
#             shares_outstanding=shares_outstanding
#         )
#         session.add(stock)
#         session.commit()

#     historical_data = generate_historical_data(
#         ticker=ticker,
#         start_price=start_price,
#         shares_outstanding=shares_outstanding,
#         start_date=start_date,
#         days=days,
#         initial_eps=initial_eps,
#         annual_dividend=annual_dividend,
#         base_volume=base_volume
#     )

#     # Insert HistoricalData
#     historical_start = start_date.date()
#     historical_end = (start_date + timedelta(days=days-1)).date()

#     for day_record in historical_data:
#         hd = HistoricalData(
#             ticker=day_record['ticker'],
#             date=datetime.strptime(day_record['date'], "%Y-%m-%d").date(),
#             open_price=day_record['open_price'],
#             close_price=day_record['close_price'],
#             day_high=day_record['day_high'],
#             day_low=day_record['day_low'],
#             week_52_high=day_record['week_52_high'],
#             week_52_low=day_record['week_52_low'],
#             trading_volume=day_record['trading_volume'],
#             average_volume=day_record['average_volume'],
#             eps=day_record['eps'],
#             p_e_ratio=day_record['p_e_ratio'],
#             dividend_yield=day_record['dividend_yield'],
#             roe=day_record['roe'],
#             debt_to_equity=day_record['debt_to_equity'],
#             revenue_growth=day_record['revenue_growth'],
#             net_income=day_record['net_income'],
#             beta=day_record['beta'],
#             standard_deviation=day_record['standard_deviation'],
#             sharpe_ratio=day_record['sharpe_ratio'],
#             RSI=day_record['RSI'],
#             moving_avg_50=day_record['moving_avg_50'],
#             moving_avg_200=day_record['moving_avg_200'],
#             MACD=day_record['MACD'],
#             analyst_rating=day_record['analyst_rating'],

#             # Set historical data range for this record
#             historical_data_start_date=historical_start,
#             historical_data_end_date=historical_end
#         )
#         session.add(hd)

#     # Update Stock info with last day's metrics
#     last_day = historical_data[-1]
#     stock.market_cap = last_day['market_cap']
#     stock.cap_category = last_day['cap_category']
#     stock.historical_data_start_date = historical_start
#     stock.historical_data_end_date = historical_end

#     # Update PriceTradingInfo
#     price_info = session.query(
#         PriceTradingInfo).filter_by(ticker=ticker).first()
#     if not price_info:
#         price_info = PriceTradingInfo(ticker=ticker)
#         session.add(price_info)

#     price_info.current_price = last_day['close_price']
#     price_info.open_price = last_day['open_price']
#     price_info.close_price = last_day['close_price']
#     price_info.day_high = last_day['day_high']
#     price_info.day_low = last_day['day_low']
#     price_info.week_52_high = last_day['week_52_high']
#     price_info.week_52_low = last_day['week_52_low']
#     price_info.trading_volume = last_day['trading_volume']
#     price_info.average_volume = last_day['average_volume']
#     price_info.historical_data_start_date = historical_start
#     price_info.historical_data_end_date = historical_end

#     # Update MarketIndicators
#     market_indicators = session.query(
#         MarketIndicators).filter_by(ticker=ticker).first()
#     if not market_indicators:
#         market_indicators = MarketIndicators(ticker=ticker)
#         session.add(market_indicators)

#     market_indicators.RSI = last_day['RSI']
#     market_indicators.moving_avg_50 = last_day['moving_avg_50']
#     market_indicators.moving_avg_200 = last_day['moving_avg_200']
#     market_indicators.MACD = last_day['MACD']
#     market_indicators.analyst_rating = last_day['analyst_rating']
#     market_indicators.historical_data_start_date = historical_start
#     market_indicators.historical_data_end_date = historical_end

#     # Update VolatilityRisk
#     volatility_risk = session.query(
#         VolatilityRisk).filter_by(ticker=ticker).first()
#     if not volatility_risk:
#         volatility_risk = VolatilityRisk(ticker=ticker)
#         session.add(volatility_risk)

#     volatility_risk.beta = last_day['beta']
#     volatility_risk.standard_deviation = last_day['standard_deviation']
#     volatility_risk.sharpe_ratio = last_day['sharpe_ratio']
#     volatility_risk.historical_data_start_date = historical_start
#     volatility_risk.historical_data_end_date = historical_end

#     # Update FundamentalMetrics (if needed)
#     fundamentals = session.query(
#         FundamentalMetrics).filter_by(ticker=ticker).first()
#     if not fundamentals:
#         fundamentals = FundamentalMetrics(ticker=ticker)
#         session.add(fundamentals)

#     # Use last day's EPS, P/E, Dividend, ROE, etc.
#     fundamentals.earnings_per_share = last_day['eps']
#     fundamentals.price_to_earnings = last_day['p_e_ratio']
#     fundamentals.dividend_yield = last_day['dividend_yield']
#     fundamentals.return_on_equity = last_day['roe']
#     fundamentals.debt_to_equity = last_day['debt_to_equity']
#     fundamentals.revenue_growth = last_day['revenue_growth']
#     fundamentals.net_income = last_day['net_income']
#     fundamentals.historical_data_start_date = historical_start
#     fundamentals.historical_data_end_date = historical_end

#     session.commit()
#     print("Historical data generated and all related tables updated successfully!")

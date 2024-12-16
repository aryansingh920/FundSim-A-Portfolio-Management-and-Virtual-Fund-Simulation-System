import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from model.model import Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators

# Database configuration
DATABASE_FILE = "data/stocks.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")
Session = sessionmaker(bind=engine)
session = Session()

def fetch_stock_data(ticker):
    """Fetch stock data from the database based on the ticker symbol."""
    try:
        stock = session.query(Stock).filter(Stock.ticker == ticker.upper()).one_or_none()
        if stock:
            return stock
        else:
            return None
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return None

def format_value(value):
    """Format numeric values with commas. If not numeric, return as is."""
    try:
        # Attempt to convert to float and format with commas
        numeric_value = float(value)
        # Decide if it's effectively an integer (no decimal places) or a float
        if numeric_value.is_integer():
            return f"{int(numeric_value):,}"
        else:
            return f"{numeric_value:,.2f}"
    except (ValueError, TypeError):
        # If conversion fails, just return the original value
        return value

def display_stock_info():
    """Display the stock information in the GUI."""
    ticker = ticker_entry.get().strip()
    if not ticker:
        messagebox.showwarning("Input Error", "Please enter a ticker symbol.")
        return

    stock = fetch_stock_data(ticker)
    if stock:
        # Clear previous data
        for widget in info_frame.winfo_children():
            widget.destroy()

        # Display basic stock information
        tk.Label(info_frame, text=f"Ticker: {stock.ticker}").pack(anchor="w")
        tk.Label(info_frame, text=f"Company Name: {stock.company_name}").pack(anchor="w")
        tk.Label(info_frame, text=f"Sector: {stock.sector}").pack(anchor="w")
        tk.Label(info_frame, text=f"Market Cap: {format_value(stock.market_cap)}").pack(anchor="w")
        tk.Label(info_frame, text=f"Cap Category: {format_value(stock.cap_category)}").pack(anchor="w")
        tk.Label(info_frame, text=f"Shares Outstanding: {format_value(stock.shares_outstanding)}").pack(anchor="w")

        # Display related information
        if stock.price_trading_info:
            tk.Label(info_frame, text="\nPrice and Trading Information:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            for info in stock.price_trading_info:
                tk.Label(info_frame, text=f"  Open Price: {format_value(info.open_price)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Close Price: {format_value(info.close_price)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Day High: {format_value(info.day_high)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Day Low: {format_value(info.day_low)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  52-Week High: {format_value(info.week_52_high)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  52-Week Low: {format_value(info.week_52_low)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Trading Volume: {format_value(info.trading_volume)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Average Volume: {format_value(info.average_volume)}").pack(anchor="w")

        if stock.fundamental_metrics:
            tk.Label(info_frame, text="\nFundamental Metrics:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            for metrics in stock.fundamental_metrics:
                tk.Label(info_frame, text=f"  EPS: {format_value(metrics.earnings_per_share)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  P/E Ratio: {format_value(metrics.price_to_earnings)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Dividend Yield: {format_value(metrics.dividend_yield)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  ROE: {format_value(metrics.return_on_equity)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Debt to Equity: {format_value(metrics.debt_to_equity)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Revenue Growth: {format_value(metrics.revenue_growth)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Net Income: {format_value(metrics.net_income)}").pack(anchor="w")

        if stock.volatility_risk:
            tk.Label(info_frame, text="\nVolatility and Risk Metrics:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            for risk in stock.volatility_risk:
                tk.Label(info_frame, text=f"  Beta: {format_value(risk.beta)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Standard Deviation: {format_value(risk.standard_deviation)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Sharpe Ratio: {format_value(risk.sharpe_ratio)}").pack(anchor="w")

        if stock.market_indicators:
            tk.Label(info_frame, text="\nMarket Sentiment and Indicators:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            for indicator in stock.market_indicators:
                tk.Label(info_frame, text=f"  RSI: {format_value(indicator.RSI)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  50-Day Moving Avg: {format_value(indicator.moving_avg_50)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  200-Day Moving Avg: {format_value(indicator.moving_avg_200)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  MACD: {format_value(indicator.MACD)}").pack(anchor="w")
                tk.Label(info_frame, text=f"  Analyst Rating: {format_value(indicator.analyst_rating)}").pack(anchor="w")
    else:
        messagebox.showinfo("No Results", f"No data found for ticker symbol '{ticker}'.")

# def main():
# Initialize the main window
root = tk.Tk()
root.title("Stock Information Viewer")

# Ticker input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Enter Ticker Symbol:").pack(side="left")
ticker_entry = tk.Entry(input_frame)
ticker_entry.pack(side="left", padx=5)
search_button = tk.Button(input_frame, text="Search", command=display_stock_info)
search_button.pack(side="left")

# Information display frame
info_frame = tk.Frame(root)
info_frame.pack(pady=10, fill="both", expand=True)


def main():
    # Start the Tkinter event loop
    root.mainloop()

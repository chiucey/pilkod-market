#!/usr/bin/env python3
"""
ONDS (Ondas Holdings) Stock Analysis Tool
Features:
1. Volume Analysis
2. Options Anomaly Detection
3. Latest News Retrieval
4. Comprehensive Analysis Report
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')


class ONDSAnalyzer:
    def __init__(self, ticker="ONDS"):
        self.ticker = yf.Ticker(ticker)
        self.ticker_symbol = ticker
        self.stock_info = self.ticker.info

    def get_volume_analysis(self, period="3mo"):
        """
        Volume Analysis
        - Fetch historical volume data
        - Calculate average volume
        - Detect unusual volume (> 2 standard deviations above mean)
        """
        print("\n" + "="*60)
        print(f"Volume Analysis for {self.ticker_symbol}")
        print("="*60)

        # Fetch historical data
        hist = self.ticker.history(period=period)

        if hist.empty:
            print("Failed to fetch historical data")
            return None

        # Basic volume statistics
        avg_volume = hist['Volume'].mean()
        max_volume = hist['Volume'].max()
        min_volume = hist['Volume'].min()
        std_volume = hist['Volume'].std()

        # Recent trading day volume
        recent_volume = hist['Volume'].iloc[-1]
        recent_5d_avg = hist['Volume'].iloc[-5:].mean()
        recent_20d_avg = hist['Volume'].iloc[-20:].mean()

        print(f"\nVolume Statistics ({period}):")
        print(f"  Average Volume: {avg_volume:,.0f}")
        print(f"  Max Volume: {max_volume:,.0f} ({hist['Volume'].idxmax().strftime('%Y-%m-%d')})")
        print(f"  Min Volume: {min_volume:,.0f}")
        print(f"  Std Dev: {std_volume:,.0f}")

        print(f"\nRecent Volume:")
        print(f"  Latest Trading Day: {recent_volume:,.0f}")
        print(f"  5-Day Average: {recent_5d_avg:,.0f}")
        print(f"  20-Day Average: {recent_20d_avg:,.0f}")

        # Unusual volume detection (mean +/- 2*std)
        threshold_high = avg_volume + 2 * std_volume
        threshold_low = avg_volume - 2 * std_volume

        unusual_days = hist[hist['Volume'] > threshold_high]

        print(f"\nUnusual Volume Detection:")
        print(f"  High Volume Threshold: {threshold_high:,.0f}")
        print(f"  Unusual Trading Days Detected: {len(unusual_days)}")

        if len(unusual_days) > 0:
            print(f"\n  Top 5 Unusual High Volume Dates:")
            for date, row in unusual_days.head().iterrows():
                print(f"    {date.strftime('%Y-%m-%d')}: {row['Volume']:,.0f} "
                      f"(Price: ${row['Close']:.2f}, Change: {((row['Close']-row['Open'])/row['Open']*100):.2f}%)")

        # Volume trend analysis
        hist['Vol_MA5'] = hist['Volume'].rolling(window=5).mean()
        hist['Vol_MA20'] = hist['Volume'].rolling(window=20).mean()

        recent_trend = "Rising" if recent_5d_avg > recent_20d_avg * 1.2 else "Falling" if recent_5d_avg < recent_20d_avg * 0.8 else "Stable"
        print(f"\nVolume Trend: {recent_trend}")

        return {
            'avg_volume': avg_volume,
            'recent_volume': recent_volume,
            'unusual_days': len(unusual_days),
            'trend': recent_trend
        }

    def get_options_analysis(self):
        """
        Options Analysis
        - Fetch options chain data
        - Analyze Put/Call ratios
        - Detect unusual options activity
        """
        print("\n" + "="*60)
        print(f"Options Analysis for {self.ticker_symbol}")
        print("="*60)

        try:
            # Get available expiration dates
            expiration_dates = self.ticker.options

            if not expiration_dates:
                print("No options data available")
                return None

            print(f"\nAvailable Expiration Dates: {len(expiration_dates)}")
            for date in expiration_dates[:5]:  # Show first 5
                print(f"  - {date}")

            # Analyze nearest expiration options
            if len(expiration_dates) > 0:
                nearest_expiry = expiration_dates[0]
                print(f"\nAnalyzing Nearest Expiration: {nearest_expiry}")

                # Get options chain
                opt_chain = self.ticker.option_chain(nearest_expiry)

                calls = opt_chain.calls
                puts = opt_chain.puts

                # Basic statistics
                total_call_volume = calls['volume'].sum()
                total_put_volume = puts['volume'].sum()
                total_call_oi = calls['openInterest'].sum()
                total_put_oi = puts['openInterest'].sum()

                # Put/Call ratios
                pc_volume_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0
                pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0

                print(f"\nVolume Statistics:")
                print(f"  Total Call Volume: {total_call_volume:,.0f}")
                print(f"  Total Put Volume: {total_put_volume:,.0f}")
                print(f"  Put/Call Volume Ratio: {pc_volume_ratio:.2f}")

                print(f"\nOpen Interest:")
                print(f"  Call Open Interest: {total_call_oi:,.0f}")
                print(f"  Put Open Interest: {total_put_oi:,.0f}")
                print(f"  Put/Call Open Interest Ratio: {pc_oi_ratio:.2f}")

                # Sentiment analysis
                if pc_volume_ratio > 1.5:
                    sentiment = "Bearish (Put volume significantly higher than Call)"
                elif pc_volume_ratio < 0.7:
                    sentiment = "Bullish (Call volume significantly higher than Put)"
                else:
                    sentiment = "Neutral"

                print(f"\nMarket Sentiment: {sentiment}")

                # Detect unusual options activity
                # Volume/Open Interest ratio > 3 is considered unusual
                calls_vol_oi_ratio = calls['volume'] / calls['openInterest'].replace(0, 1)
                puts_vol_oi_ratio = puts['volume'] / puts['openInterest'].replace(0, 1)

                unusual_calls = calls[calls_vol_oi_ratio > 3]
                unusual_puts = puts[puts_vol_oi_ratio > 3]

                print(f"\nUnusual Options Activity (Volume/OI > 3):")
                print(f"  Unusual Call Contracts: {len(unusual_calls)}")
                print(f"  Unusual Put Contracts: {len(unusual_puts)}")

                if len(unusual_calls) > 0:
                    print(f"\n  Top 3 Unusual Call Contracts:")
                    for _, row in unusual_calls.head(3).iterrows():
                        print(f"    Strike: ${row['strike']:.2f} | Volume: {row['volume']:.0f} | "
                              f"Open Interest: {row['openInterest']:.0f} | IV: {row.get('impliedVolatility', 0)*100:.2f}%")

                if len(unusual_puts) > 0:
                    print(f"\n  Top 3 Unusual Put Contracts:")
                    for _, row in unusual_puts.head(3).iterrows():
                        print(f"    Strike: ${row['strike']:.2f} | Volume: {row['volume']:.0f} | "
                              f"Open Interest: {row['openInterest']:.0f} | IV: {row.get('impliedVolatility', 0)*100:.2f}%")

                return {
                    'pc_volume_ratio': pc_volume_ratio,
                    'pc_oi_ratio': pc_oi_ratio,
                    'sentiment': sentiment,
                    'unusual_calls': len(unusual_calls),
                    'unusual_puts': len(unusual_puts)
                }

        except Exception as e:
            print(f"Failed to fetch options data: {str(e)}")
            return None

    def get_latest_news(self):
        """
        Get Latest News
        - Fetch news from multiple sources
        - Analyze news sentiment
        """
        print("\n" + "="*60)
        print(f"Latest News for {self.ticker_symbol}")
        print("="*60)

        news_list = []

        try:
            # Method 1: Try to get news from yfinance
            news = self.ticker.news

            valid_news_count = 0
            if news and len(news) > 0:
                print(f"\nRetrieved {len(news)} news from Yahoo Finance")

                for i, item in enumerate(news[:10], 1):
                    title = item.get('title', 'N/A')
                    publisher = item.get('publisher', 'N/A')
                    pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                    link = item.get('link', '')

                    # Skip invalid news
                    if not title or title == 'N/A' or not link:
                        continue

                    valid_news_count += 1
                    print(f"\n  {valid_news_count}. {title}")
                    print(f"     Source: {publisher} | Time: {pub_time.strftime('%Y-%m-%d %H:%M')}")
                    print(f"     Link: {link}")

                    news_list.append({
                        'title': title,
                        'publisher': publisher,
                        'time': pub_time,
                        'link': link
                    })

                if valid_news_count == 0:
                    print("Yahoo Finance news titles empty, trying other sources...")
                    news_list = []  # Clear invalid news

            # Method 2: If yfinance has no news, use web search
            if len(news_list) == 0:
                print("\nYahoo Finance news empty, searching for latest news...")
                web_news = self._search_web_news()
                if web_news:
                    news_list = web_news

        except Exception as e:
            print(f"Failed to fetch news: {str(e)}")
            if not news_list:
                web_news = self._search_web_news()
                if web_news:
                    news_list = web_news

        # Simple keyword-based sentiment analysis
        if news_list:
            positive_keywords = ['surge', 'rise', 'gain', 'up', 'bull', 'positive', 'beat', 'growth', 'upside', 'upgrade']
            negative_keywords = ['drop', 'fall', 'decline', 'down', 'bear', 'negative', 'miss', 'loss', 'downgrade', 'risk']

            positive_count = 0
            negative_count = 0

            for news_item in news_list:
                title_lower = news_item['title'].lower()
                if any(kw in title_lower for kw in positive_keywords):
                    positive_count += 1
                if any(kw in title_lower for kw in negative_keywords):
                    negative_count += 1

            total = len(news_list)
            if positive_count > negative_count:
                news_sentiment = "Mostly Positive"
            elif negative_count > positive_count:
                news_sentiment = "Mostly Negative"
            else:
                news_sentiment = "Neutral"

            print(f"\nNews Sentiment Analysis:")
            print(f"  Positive News: {positive_count}/{total}")
            print(f"  Negative News: {negative_count}/{total}")
            print(f"  Overall Sentiment: {news_sentiment}")

            return {
                'news_count': len(news_list),
                'positive': positive_count,
                'negative': negative_count,
                'sentiment': news_sentiment
            }
        else:
            print("\nNo news data available")
            return None

    def _search_web_news(self):
        """Fetch latest news using web search"""
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse

        print(f"\nSearching for latest news about {self.ticker_symbol}...")

        news_list = []

        # Method 1: Try Google Finance page
        try:
            url = f"https://www.google.com/finance/quote/{self.ticker_symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find news section
                news_section = soup.find('div', {'class': 'IoD0Be'})
                if news_section:
                    news_items = news_section.find_all('div', {'class': 'MFcq1e'})[:10]

                    if news_items:
                        print(f"\nRetrieved {len(news_items)} news from Google Finance")

                        for i, item in enumerate(news_items, 1):
                            title_elem = item.find('div', {'class': 'YB2lIf'})
                            link_elem = item.find('a')
                            time_elem = item.find('div', {'class': 'fz86Mu'})

                            if title_elem:
                                title = title_elem.text.strip()
                                link = link_elem.get('href', '') if link_elem else ''
                                time = time_elem.text.strip() if time_elem else 'N/A'

                                print(f"\n  {i}. {title}")
                                print(f"     Time: {time}")
                                print(f"     Link: {link}")

                                news_list.append({
                                    'title': title,
                                    'publisher': 'Google Finance',
                                    'time': datetime.now(),
                                    'link': link
                                })

                        return news_list
        except Exception as e:
            print(f"Google Finance fetch failed: {str(e)}")

        # Method 2: Provide financial website links for manual viewing
        print(f"\nAutomatic news retrieval limited. Manual news sources for {self.ticker_symbol}:")
        print(f"\nRecommended Sources:")
        print(f"  1. Yahoo Finance: https://finance.yahoo.com/quote/{self.ticker_symbol}/")
        print(f"  2. Google Finance: https://www.google.com/finance/quote/{self.ticker_symbol}")
        print(f"  3. Seeking Alpha: https://seekingalpha.com/symbol/{self.ticker_symbol}")
        print(f"  4. StockTwits (Investor Discussion): https://stocktwits.com/{self.ticker_symbol}")
        print(f"  5. MarketWatch: https://www.marketwatch.com/investing/stock/{self.ticker_symbol.lower()}")

        return None

    def _get_alternative_news(self):
        """Alternative news retrieval method"""
        print("\nTrying alternative news sources...")
        print(f"\nYou can manually check latest news for {self.ticker_symbol}:")
        print(f"  - Yahoo Finance: https://finance.yahoo.com/quote/{self.ticker_symbol}/")
        print(f"  - Google Finance: https://www.google.com/finance/quote/{self.ticker_symbol}")
        print(f"  - Seeking Alpha: https://seekingalpha.com/symbol/{self.ticker_symbol}")
        print(f"  - StockTwits: https://stocktwits.com/{self.ticker_symbol}")

    def get_company_info(self):
        """
        Get Company Basic Information and Financial Data
        """
        print("\n" + "="*60)
        print(f"Company Information for {self.ticker_symbol}")
        print("="*60)

        info = self.stock_info

        print(f"\nBasic Information:")
        print(f"  Company Name: {info.get('shortName', 'N/A')}")
        print(f"  Industry: {info.get('industry', 'N/A')}")
        print(f"  Sector: {info.get('sector', 'N/A')}")
        print(f"  Current Price: ${info.get('currentPrice', 'N/A')}")
        print(f"  Market Cap: ${info.get('marketCap', 0)/1_000_000:,.2f}M")

        print(f"\nFinancial Metrics:")
        print(f"  Revenue (TTM): ${info.get('totalRevenue', 0)/1_000_000:,.2f}M")
        print(f"  Net Profit Margin: {info.get('profitMargins', 0)*100:.2f}%")
        print(f"  P/E Ratio: {info.get('trailingPE', 'N/A')}")
        print(f"  52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
        print(f"  52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")

        print(f"\nAnalyst Ratings:")
        target_mean = info.get('targetMeanPrice', 0)
        current = info.get('currentPrice', 0)
        if target_mean and current:
            upside = (target_mean - current) / current * 100
            print(f"  Target Price (Mean): ${target_mean:.2f}")
            print(f"  Expected Change: {upside:.2f}%")

        return info

    def generate_report(self, period="3mo"):
        """
        Generate Comprehensive Analysis Report
        """
        print("\n" + "#"*60)
        print(f"# Comprehensive Analysis Report for {self.ticker_symbol}")
        print("#" + f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#"*60)

        # Get all analysis
        company_info = self.get_company_info()
        volume_data = self.get_volume_analysis(period=period)
        options_data = self.get_options_analysis()
        news_data = self.get_latest_news()

        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)

        print(f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Current Price: ${company_info.get('currentPrice', 'N/A')}")
        print(f"Volume Status: {volume_data['trend'] if volume_data else 'N/A'}")

        if options_data:
            print(f"Options Sentiment: {options_data['sentiment']}")
            print(f"Put/Call Ratio: {options_data['pc_volume_ratio']:.2f}")

        if news_data:
            print(f"News Sentiment: {news_data['sentiment']}")

        print("\nDisclaimer:")
        print("  This analysis is for reference only and does not constitute investment advice.")
        print("  Stock investing involves risk; trade carefully.")
        print("="*60 + "\n")


def main():
    """
    Main Function
    """
    import argparse

    parser = argparse.ArgumentParser(description='Stock Analyzer - Analyze US stock volume, options anomalies, and latest news')
    parser.add_argument('--ticker', type=str, required=True, help='Stock symbol (e.g., ONDS, AAPL, TSLA)')
    parser.add_argument('--period', type=str, default='3mo',
                        choices=['1mo', '3mo', '6mo', '1y'],
                        help='Historical data range (default: 3mo)')

    args = parser.parse_args()

    print(f"Starting Stock Analyzer - Analyzing {args.ticker}...")

    # Create analyzer
    analyzer = ONDSAnalyzer(args.ticker)

    # Generate comprehensive report
    analyzer.generate_report(period=args.period)

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{args.ticker}_analysis_{timestamp}.txt"

    print(f"To save the report, manually copy above content or take a screenshot")
    print(f"Report Timestamp: {timestamp}")


if __name__ == "__main__":
    main()

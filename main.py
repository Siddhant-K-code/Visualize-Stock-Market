# Stock Market

# Imports
import yfinance
import json
import readchar
import time
import locale

# Assign contents of json to dict
with open("tickers.json", "r") as tickers_json:
    ticker_data = json.load(tickers_json)

# Clear console
def clear():
    print("\033c", end = "")

# Set locale for currency
locale.setlocale(locale.LC_ALL, '')

# RGB ANSI formatter
def rgb(rgb_list):
    r = rgb_list[0]
    g = rgb_list[1]
    b = rgb_list[2]
    return f"\033[38;2;{r};{g};{b}m"

# Search dict for query
def search(query):
    results = []
    for key in ticker_data:
        if len(results) <= 25:
            if query.lower() in key.lower() or query.lower() in ticker_data[key].lower():
                results.append(key)
        else:
            break
    return results

# Format search result
def search_result(result):
    info = ticker_data[result] if len(ticker_data[result]) <= 50 else f"{ticker_data[result][:46]} ..."
    return f"{result} - {info}"

# Search by ticker
def stock_search():
    query = []
    while 1:
        clear()
        print("Search by ticker: ", end = "")
        print("".join(query), end = "\n\n")
        if len(query):
            for result in search("".join(query)):
                print(search_result(result))
        key = readchar.readkey()
        if key == "\r": # Enter
            break
        elif key == "\x7f": # Backspace
            try:
                query.pop(-1)
            except:
                pass
        else:
            query.append(key)
    return "".join(query)

# Check if query exists in ticker json
def check_query(query):
    try: 
        ticker_data[query.upper()]
        return True
    except:
        return False

# Format money
def fm(value):
    return locale.currency(value, symbol = False, grouping = True)

days_to_scale = {
    5 : 4,
    10 : 2
}

# Unicode blocks 
block = "█"
half_block = "▄"

# ANSI Colors/Codes
green = rgb([56, 255, 75])
red = rgb([252, 36, 3])
reset = "\033[0m"


# Generate graph for stock
def stock_entry(ticker, days):
    si = [f"\nTicker: {ticker.upper()}"] 
    days = days if days < 60 else 60

    # Graph
    try:
        stock = yfinance.Ticker(ticker)
        history = stock.history(period = f"{days}d")
    
        increment_x = 1
        try:
            increment_x = days_to_scale[days]
        except:
            pass

        # All open and close data
        start_date = str(history.index[0]).split()[0]
        end_date = str(history.index[-1]).split()[0]
        stock_closes = []
        for i in range(len(history["Open"])):
            stock_closes.append(history["Open"][i])
            stock_closes.append(history["Close"][i])

        si.append(f"\nPrevious Open: {green}{fm(stock_closes[-2])}{reset} USD")
        si.append(f"Previous Close: {green}{fm(stock_closes[-1])}{reset} USD") 
        difference = round((stock_closes[-1] / stock_closes[-2] - 1) * 100, 3)
        si.append(f"Percent Change: {green if difference >= 0 else red}{difference}{reset} %")

        change = stock_closes[-1] - stock_closes[0]
        close_max = max(stock_closes)
        close_min = min(stock_closes)
        close_range = close_max - close_min
        offset = len(str(int(close_max))) + 3
        # Y-axis increments for graph
        increments_y = [str(round(close_min + close_range * (i/10), 2)).ljust(offset, "0") for i in range(11)]
        
        # Building the graph
        graph = []
        for i in range(21):
            graph.append([])
            if i % 2 == 0:
                graph[i].append(increments_y[::-1][i // 2])
            else:
                graph[i].append("".ljust(offset))
            graph[i].append(" | ")
        graph.append(["".ljust(offset + 1), "└ ", "─".ljust(2) * (days + 1)])
        graph.append(["".ljust(offset + 3), start_date, str(end_date).rjust(days * 2 - len(start_date))])
        
        for close in stock_closes:
            for i in range(21):
                if close >= close_min + close_range * (i/20):
                    graph[20 - i].append(f"{green if change >= 0 else red}{block}{reset}" * increment_x)
                elif close >= close_min + close_range * (i/20) - close_range / 40:
                    graph[20 - i].append(f"{green if change >= 0 else red}{half_block}{reset}" * increment_x)
                else:
                    graph[20 - i].append(" " * increment_x)

        for row in graph:
            print("".join(row))
            time.sleep(0.03)
    except:
        print("No graph")

    try:
        stock_info = stock.info
        currency = stock_info["currency"]

        # Trying each piece of data
        try:
            si.insert(1, f"Name: {stock_info['shortName']}")
        except:
            si.insert(1, f"Name: {ticker_data[ticker.upper()]}")
        try:
            si.insert(2, f"Sector: {stock_info['sector']}, {stock_info['industry']}")
        except:
            si.insert(2, "Sector: ---")
        try:
            si.append(f"\nMarket Cap: {green}{fm(stock_info['marketCap'])}{reset} {currency}")
        except:
            si.append("\nMarket Cap: ---")
        try:
            si.append(f"Regular Market Volume: {green}{fm(stock_info['regularMarketVolume'])}{reset} ")
        except:
            si.append("Regular Market Volume: ---")
        try:
            si.append(f"\n200 Day Average: {green}{fm(stock_info['twoHundredDayAverage'])}{reset} {currency}")
        except:
            si.append("\n200 Day Average: ---")
        try:
            si.append(f"50 Day Average: {green}{fm(stock_info['fiftyDayAverage'])}{reset} {currency}")
        except:
            si.append("50 Day Average: ---")
        try:
            si.append(f"\nTrailing P/E: {green}{stock_info['trailingPE']}{reset}")
        except:
            si.append("\nTrailing P/E: ---")
        try:
            if stock_info['forwardPE']:
                si.append(f"Forward P/E: {green}{stock_info['forwardPE']}{reset}")
            else:
                raise Exception()
        except:
            si.append("Forward P/E: ---")
        
        
    except:
        si.insert(1, f"Name: {ticker_data[ticker.upper()]}")

    for line in si:
        print(line)
        time.sleep(0.03)

def loop():
    while 1:
        clear()
        result = stock_search()
        clear()
        if check_query(result):
            stock_entry(result, 30)
        else:
            print("No stocks found")
        print("\nSearch again (y/n):")
        cont = readchar.readkey()
        if cont == "n":
            break

loop()




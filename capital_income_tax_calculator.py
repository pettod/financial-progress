import csv
import pandas as pd
import numpy as np


STOCK_CSV_FILE = "nordnet-ostoerittain.csv"
DIVIDEND_CSV_FILE = "transactions_export.csv"
BASE_TAX_PERCENTAGE = 30
MARGIN_TAX_PERCENTAGE = 34
MARGIN_TAX_THRESHOLD = 50000
ZERO_TAX_THRESHOLD = 1000
N_YEARS_LOSSES_ACCUMULATED = 5
STOCK_NAMING_CONVERSION = {  # Define here the headers in CSV file
    "sell_date": "Luovutusaika",
    "profit": "Voitto tai tappio EUR",
    "buy_cost": "Hankintakulut EUR",
    "sell_cost": "Myyntikulut EUR",
}
DIVIDEND_NAMING_CONVERSION = {  # Define here the headers in CSV file
    "date": "Maksupäivä",
    "profit": "Summa",
    "transaction_type": "Tapahtumatyyppi",
    "dividend": "OSINKO",
    "tax": "ENNAKKOPIDÄTYS",
}


def taxAmount(earnings):
    # Calculate earning based on previous years losses
    previous_years_earnings = sum(earnings[-N_YEARS_LOSSES_ACCUMULATED:-1])
    earning = earnings[-1]
    if previous_years_earnings < 0:
        earning += previous_years_earnings

    # Calculate tax for earning
    if earning > MARGIN_TAX_THRESHOLD:
        base_tax = BASE_TAX_PERCENTAGE * MARGIN_TAX_THRESHOLD
        margin_tax = MARGIN_TAX_PERCENTAGE * (earning - MARGIN_TAX_THRESHOLD)
        tax = (base_tax + margin_tax) / 100
    elif earning <= ZERO_TAX_THRESHOLD:
        tax = 0
    else:
        tax = BASE_TAX_PERCENTAGE * earning / 100
    return tax


def printTable(texts, values):
    # Compute header length
    text_lengths = []
    for i, text in enumerate(texts):
        text_lengths.append(5 if i == 0 else max(9, len(text)))
    table_length = sum(text_lengths) + 4 + 3 * max(0, len(text_lengths) - 1)

    # Print header
    print(table_length * "-")
    print("| ", end="")
    for i, text in enumerate(texts):
        number_of_spaces = max(0, text_lengths[i] - len(text))
        print("{}{}".format(" " * number_of_spaces, text), end=" | ")

    # Print table
    print("\n" + table_length * "-")
    for i in range(len(values[0])):
        if i == len(values[0]) - 1:
            print(table_length * "-")
        print("| ", end="")
        for j in range(len(values)):
            value = values[j][i]
            if type(value) == np.float64:
                value = "{0:.2f}".format(value)
            number_of_spaces = max(0, text_lengths[j] - len(str(value)))
            print("{}{}".format(" " * number_of_spaces, value), end=" | ")
        print()
    print(table_length * "-")


def main():
    snc = STOCK_NAMING_CONVERSION
    dnc = DIVIDEND_NAMING_CONVERSION

    # Read CSV
    stock_df = pd.read_csv(
        STOCK_CSV_FILE, header=0, sep="\t", encoding="utf-16", decimal=",")
    dividend_df = pd.read_csv(
        DIVIDEND_CSV_FILE, header=0, sep="\t", encoding="utf-16", decimal=",")
    stock_df[snc["sell_date"]] = pd.to_datetime(
        stock_df[snc["sell_date"]], format="%d.%m.%Y")
    dividend_df[dnc["date"]] = pd.to_datetime(
        dividend_df[dnc["date"]], format="%Y.%m.%d")
    min_year_stock = min(stock_df[snc["sell_date"]]).year
    max_year_stock = max(stock_df[snc["sell_date"]]).year
    min_year_dividend = min(dividend_df[dnc["date"]]).year
    max_year_dividend = max(dividend_df[dnc["date"]]).year
    min_year = min(min_year_stock, min_year_dividend)
    max_year = max(max_year_stock, max_year_dividend)

    # Process annual info
    years = list(range(min_year, max_year + 1))
    buy_costs = []
    sell_costs = []
    losses = []
    profits = []
    dividends = []
    dividend_taxes = []
    earnings = []
    taxes = []
    net_earnings = []
    for year in years:
        rows_stock = stock_df[
            (stock_df[snc["sell_date"]] > f"01-01-{year}") &
            (stock_df[snc["sell_date"]] < f"31-12-{year}")
        ]
        rows_dividend = dividend_df[
            (dividend_df[dnc["date"]] > f"01-01-{year}") &
            (dividend_df[dnc["date"]] < f"31-12-{year}")
        ]
        buy_cost = rows_stock[snc["buy_cost"]].astype(float).to_numpy().sum()
        sell_cost = rows_stock[snc["sell_cost"]].astype(float).to_numpy().sum()
        loss = abs(rows_stock[rows_stock[snc["profit"]] < 0][
            snc["profit"]].to_numpy().sum())
        profit = rows_stock[rows_stock[snc["profit"]] >= 0][
            snc["profit"]].to_numpy().sum()
        dividend = rows_dividend[
            rows_dividend[dnc["transaction_type"]] ==
            dnc["dividend"]][dnc["profit"]].to_numpy().astype(np.float64).sum()
        dividend_tax = abs(rows_dividend[rows_dividend[
            dnc["transaction_type"]] ==
            dnc["tax"]][dnc["profit"]].to_numpy().astype(np.float64).sum())
        earning = profit - buy_cost - sell_cost - loss
        earnings.append(earning)
        tax = taxAmount(earnings)
        net_earning = earning - tax
        buy_costs.append(buy_cost)
        sell_costs.append(sell_cost)
        profits.append(profit)
        dividends.append(dividend)
        dividend_taxes.append(dividend_tax)
        losses.append(loss)
        taxes.append(tax)
        net_earnings.append(net_earning)

    # Add dividends to earnings after tax calculations because dividends are
    # already taxed immediately when you receive them
    taxes = [a + b for (a, b) in zip(taxes, dividend_taxes)]
    earnings = [a + b + c for (a, b, c) in zip(
        earnings, dividends, dividend_taxes)]
    net_earnings = [a + b for (a, b) in zip(net_earnings, dividends)]

    # Print
    texts = [
        "Year",
        "Buy cost",
        "Sell cost",
        "Loss",
        "Profit",
        "Dividend",
        "Earning",
        "Tax",
        "Net earning"
    ]
    values = [
        years + ["Total"],
        buy_costs,
        sell_costs,
        losses,
        profits,
        dividends,
        earnings,
        taxes,
        net_earnings,
    ]
    for i in range(1, len(values)):
        values[i].append(sum(values[i]))
    printTable(texts, values)


main()

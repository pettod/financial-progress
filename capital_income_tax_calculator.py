import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


CSV_FILE_NAME = "nordnet-ostoerittain.csv"
BASE_TAX_PERCENTAGE = 30
MARGIN_TAX_PERCENTAGE = 34
MARGIN_TAX_THRESHOLD = 50000


def taxAmount(profit):
    if profit > MARGIN_TAX_THRESHOLD:
        base_tax = BASE_TAX_PERCENTAGE * MARGIN_TAX_THRESHOLD
        margin_tax = MARGIN_TAX_PERCENTAGE * (profit - MARGIN_TAX_THRESHOLD)
        tax = (base_tax + margin_tax) / 100
    elif profit <= 0:
        tax = 0
    else:
        tax = BASE_TAX_PERCENTAGE * profit / 100
    return tax


def main():
    # Read CSV
    csv_file = pd.read_csv(
        CSV_FILE_NAME, header=0, sep="\t", encoding="utf-16", decimal=",")
    csv_file["Luovutusaika"] = pd.to_datetime(
        csv_file["Luovutusaika"], format="%d.%m.%Y")
    min_year = min(csv_file["Luovutusaika"]).year
    max_year = max(csv_file["Luovutusaika"]).year

    # Process annual info
    years = list(range(min_year, max_year + 1))
    buy_costs = []
    sell_costs = []
    losses = []
    profits = []
    earnings = []
    taxes = []
    for year in years:
        rows = csv_file[
            (csv_file["Luovutusaika"] > f"01-01-{year}") &
            (csv_file["Luovutusaika"] < f"31-12-{year}")
        ]
        loss = rows[rows["Voitto tai tappio EUR"] < 0]["Voitto tai tappio EUR"].to_numpy().sum()
        profit = rows[rows["Voitto tai tappio EUR"] >= 0]["Voitto tai tappio EUR"].to_numpy().sum()
        buy_cost = rows["Hankintakulut EUR"].astype(float).to_numpy().sum()
        sell_cost = rows["Myyntikulut EUR"].astype(float).to_numpy().sum()
        earning = profit - buy_cost - sell_cost + loss
        buy_costs.append(buy_cost)
        sell_costs.append(sell_cost)
        profits.append(profit)
        losses.append(loss)
        earnings.append(earning)
        taxes.append(taxAmount(earning))

    # Print
    texts = [
        "Year",
        "Buy cost",
        "Sell cost",
        "Loss",
        "Profit",
        "Earning",
        "Tax",
    ]
    values = [
        years + ["Total"],
        buy_costs,
        sell_costs,
        losses,
        profits,
        earnings,
        taxes,
    ]
    for i in range(1, len(values)):
        values[i].append(sum(values[i]))
    text_lengths = []
    for i, text in enumerate(texts):
        text_lengths.append(5 if i == 0 else max(9, len(text)))
    table_length = sum(text_lengths) + 4 + 3 * max(0, len(text_lengths) - 1)
    print(table_length * "-")
    print("| ", end="")
    for i, text in enumerate(texts):
        number_of_spaces = max(0, text_lengths[i] - len(text))
        print("{}{}".format(" " * number_of_spaces, text), end=" | ")
    print("\n" + table_length * "-")
    for i in range(len(taxes)):
        if i == len(taxes) - 1:
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


main()

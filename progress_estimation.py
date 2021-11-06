import matplotlib.pyplot as plt
import sys


START_EQUITY = int(sys.argv[1])
MONTHLY_SAVIGS = int(sys.argv[2])
MONTHLY_SAVIGS_ANNUAL_INCREASE_PERCENT = 7
ANNUAL_RETURN_EXPECTATION_PERCENT = 25
MAX_INVEST_YEARS = 20


def main():
    monthly_return_expectation = \
        (1 + ANNUAL_RETURN_EXPECTATION_PERCENT / 100) ** (1 / float(12))
    equity = START_EQUITY
    monthly_equities = [START_EQUITY]
    annual_equities = [START_EQUITY]
    annual_savings = [START_EQUITY]
    savings = START_EQUITY
    for i in range(MAX_INVEST_YEARS):
        monthly_savigs = (1 + i * MONTHLY_SAVIGS_ANNUAL_INCREASE_PERCENT / 100) * MONTHLY_SAVIGS
        for j in range(12):
            equity *= monthly_return_expectation
            equity += monthly_savigs
            savings += monthly_savigs
            monthly_equities.append(equity)
        annual_equities.append(equity)
        annual_savings.append(savings)

    # Million
    months_to_million = 0
    money_after_million = 0
    for m, e in enumerate(monthly_equities):
        if e >= 1_000_000:
            months_to_million = m
            money_after_million = e
            break
    years_to_million = months_to_million / 12
    print("Years to million:", years_to_million)

    table_data = []
    for i in range(len(annual_equities)):
        table_data.append([i, "{:,.0f}".format(int(annual_equities[i]))])

    years = list(range(MAX_INVEST_YEARS + 1))
    plt.subplot(1, 2, 1)
    plt.plot(years, annual_equities, label="Investments")
    plt.plot(years, annual_savings, label="Savings")
    plt.plot(years_to_million, money_after_million, "go")
    plt.gca().set_yticklabels(["{:,.0f}".format(x) for x in plt.gca().get_yticks()])
    plt.legend()
    plt.xlabel("Years")
    plt.ylabel("Euros (€)")

    plt.subplot(1, 2, 2)
    plt.axis("off")
    plt.table(cellText=table_data, loc="center", colLabels=["Year", "Equity"])

    plt.suptitle("Financial progress estimation")
    plt.show()


main()

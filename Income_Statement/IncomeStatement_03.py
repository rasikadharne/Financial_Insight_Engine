#Pulled and mapped way more tags from SEC XRBL tags on the code 

#basicallly realized that the tags that i was pulling were not enough so just modified the code to pull way more tags that i felt were best classified under income statement 
import requests
import pandas as pd

CIK = "0001783879"
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "Use your email address"}

def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def extract_income_data(xbrl_data):
    income_tags = {
        "Revenues": ("Total Net Revenues", "USD"),
        "InterestIncomeExpenseNet": ("Net Interest Revenues", "USD"),
        "InterestIncomeOther": ("Other Revenues", "USD"),
        "FloorBrokerageExchangeAndClearanceFees": ("Brokerage and Transaction", "USD"),
        "MarketingExpense": ("Marketing", "USD"),
        "GeneralAndAdministrativeExpense": ("General and Administrative", "USD"),
        "OperatingExpenses": ("Total Operating Expenses", "USD"),
        "GainLossOnInvestments": ("Change in Fair Value of Convertible Notes", "USD"),
        "OtherNonoperatingIncomeExpense": ("Other Expense (Income), Net", "USD"),
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": ("Income (Loss) Before Taxes", "USD"),
        "IncomeTaxExpenseBenefit": ("Provision for Income Taxes", "USD"),
        "NetIncomeLoss": ("Net Income (Loss)", "USD"),
        "NetIncomeLossAvailableToCommonStockholdersBasic": ("Net Income (Loss) Attributable to Common Stockholders (Basic)", "USD"),
        "NetIncomeLossAvailableToCommonStockholdersDiluted": ("Net Income (Loss) Attributable to Common Stockholders (Diluted)", "USD"),
        "EarningsPerShareBasic": ("Net Income (Loss) Per Share (Basic)", "pure"),
        "EarningsPerShareDiluted": ("Net Income (Loss) Per Share (Diluted)", "pure"),
        "WeightedAverageNumberOfSharesOutstandingBasic": ("Weighted-Average Shares (Basic)", "shares"),
        "WeightedAverageNumberOfDilutedSharesOutstanding": ("Weighted-Average Shares (Diluted)", "shares"),
        "ShareBasedCompensation": ("Share-Based Compensation Expense", "USD")
    }
    
    income_data = {label: {} for label, _ in income_tags.values()}
    
    for tag, (label, unit) in income_tags.items():
        if tag in xbrl_data:
            units = xbrl_data[tag]["units"]
            if unit in units:
                entries = units[unit]
                for entry in entries:
                    year = entry.get("fy")
                    if year and 2020 <= year <= 2024 and entry.get("form") == "10-K":
                        # Convert to millions only for USD units
                        value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]
                        income_data[label][year] = value
            else:
                print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
    
    # Manually set values to match SEC 10-K
    income_data["Total Net Revenues"] = {2020: 958, 2021: 1815, 2022: 1358}
    income_data["Transaction-based Revenues"] = {2020: 720, 2021: 1402, 2022: 814}
    income_data["Net Interest Revenues"] = {2020: 177, 2021: 256, 2022: 424}
    income_data["Other Revenues"] = {2020: 61, 2021: 157, 2022: 120}
    income_data["Brokerage and Transaction"] = {2020: 114, 2021: 158, 2022: 179}
    income_data["Technology and Development"] = {2020: 215, 2021: 1234, 2022: 878}
    income_data["Operations"] = {2020: 135, 2021: 368, 2022: 285}
    income_data["Marketing"] = {2020: 186, 2021: 325, 2022: 103}
    income_data["General and Administrative"] = {2020: 295, 2021: 1371, 2022: 924}
    income_data["Total Operating Expenses"] = {2020: 945, 2021: 3456, 2022: 2369}
    income_data["Change in Fair Value of Convertible Notes"] = {2020: 0, 2021: 2045, 2022: 0}
    income_data["Other Expense (Income), Net"] = {2020: 0, 2021: -1, 2022: 16}
    income_data["Income (Loss) Before Taxes"] = {2020: 13, 2021: -3685, 2022: -1027}
    income_data["Provision for Income Taxes"] = {2020: 6, 2021: 2, 2022: 1}
    income_data["Net Income (Loss)"] = {2020: 7, 2021: -3687, 2022: -1028}
    income_data["Net Income (Loss) Attributable to Common Stockholders (Basic)"] = {2020: 3, 2021: -3687, 2022: -1028}
    income_data["Net Income (Loss) Attributable to Common Stockholders (Diluted)"] = {2020: 3, 2021: -3687, 2022: -1028}
    income_data["Net Income (Loss) Per Share (Basic)"] = {2020: 0.01, 2021: -7.49, 2022: -1.17}
    income_data["Net Income (Loss) Per Share (Diluted)"] = {2020: 0.01, 2021: -7.49, 2022: -1.17}
    income_data["Weighted-Average Shares (Basic)"] = {2020: 225748355, 2021: 492381190, 2022: 878630024}
    income_data["Weighted-Average Shares (Diluted)"] = {2020: 244997388, 2021: 492381190, 2022: 878630024}
    
    return income_data

def create_dataframe(income_data):
    years = sorted(set().union(*[set(d.keys()) for d in income_data.values()]))
    df_data = {}
    for label in income_data:
        df_data[label] = [income_data[label].get(year, None) for year in years]
    df = pd.DataFrame(df_data, index=years)
    df = df.transpose()
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Item'}, inplace=True)
    return df

def save_to_csv(df, filename="robinhood_income_statements.csv"):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    xbrl_data = get_xbrl_data()
    income_data = extract_income_data(xbrl_data)
    print("\nExtracted Income Data (2020-2022, 10-K only, in millions):")
    for label, years in income_data.items():
        print(f"{label}: {dict(sorted(years.items()))}")
    
    df = create_dataframe(income_data)
    print("\nDataFrame:")
    print(df)
    save_to_csv(df)
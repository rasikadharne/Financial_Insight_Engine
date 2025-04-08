#experimenting with code, hardcoded some of the values for tags as
#the data that was pulled from SEC didnt match Yahoo and WSJ websites. 

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
        "Revenues": "Total Net Revenues",
        "InterestIncomeExpenseNet": "Net Interest Revenues",
        "InterestIncomeOther": "Other Revenues",  # Adjust based on tag list
        "FloorBrokerageExchangeAndClearanceFees": "Brokerage and Transaction",
        "MarketingExpense": "Marketing",
        "GeneralAndAdministrativeExpense": "General and Administrative",
        "OperatingExpenses": "Total Operating Expenses",
        "GainLossOnInvestments": "Change in Fair Value of Convertible Notes",
        "OtherNonoperatingIncomeExpense": "Other Expense (Income), Net",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "Income (Loss) Before Taxes",
        "IncomeTaxExpenseBenefit": "Provision for Income Taxes",
        "NetIncomeLoss": "Net Income (Loss)"
    }
    
    income_data = {label: {} for label in income_tags.values()}
    
    for tag, label in income_tags.items():
        if tag in xbrl_data:
            entries = xbrl_data[tag]["units"]["USD"]
            print(f"{label} has {len(entries)} entries in total.")
            for entry in entries:
                year = entry.get("fy")
                if year and 2020 <= year <= 2024 and entry.get("form") == "10-K":
                    income_data[label][year] = entry["val"] / 1_000_000
    
    # Derive Transaction-based Revenues, Other Revenues, Tech and Dev, Operations
    for year in income_data["Total Net Revenues"]:
        total_revenues = income_data["Total Net Revenues"].get(year, 0)
        net_interest = income_data["Net Interest Revenues"].get(year, 0)
        other_revenues = income_data["Other Revenues"].get(year, 0)
        total_op_exp = income_data["Total Operating Expenses"].get(year, 0)
        brokerage = income_data["Brokerage and Transaction"].get(year, 0)
        marketing = income_data["Marketing"].get(year, 0)
        g_and_a = income_data["General and Administrative"].get(year, 0)
        
        # Derive Transaction-based Revenues
        transaction_based = total_revenues - net_interest - other_revenues
        income_data.setdefault("Transaction-based Revenues", {})[year] = transaction_based
        
        # Derive Technology and Development and Operations
        tech_dev = 0  # Placeholder; adjust based on SEC data
        operations = 0  # Placeholder; adjust based on SEC data
        income_data.setdefault("Technology and Development", {})[year] = tech_dev
        income_data.setdefault("Operations", {})[year] = operations
    
    # Manually set values to match SEC 10-K (temporary until we find correct tags)
    #as i was having issues pulling the right values when i cross checked
    income_data["Transaction-based Revenues"] = {2020: 720, 2021: 1402, 2022: 814}
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
    print("\nExtracted Income Data (2020-2024, 10-K only, in millions):")
    for label, years in income_data.items():
        print(f"{label}: {dict(sorted(years.items()))}")
    
    df = create_dataframe(income_data)
    print("\nDataFrame:")
    print(df)
    save_to_csv(df)
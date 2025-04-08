#Aim is to pull infomration from income statement of 10-K filed by companies with SEC
#the aim is to use XBRL tags 
import requests
import pandas as pd

CIK = "0001783879"
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "use your email address"}

#Get the financial data for a CIK 
def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

#Get the tags once confirmed that the response has FACTS and us- GAPP dictionaries within data 
def extract_income_data(xbrl_data):
    income_tags = {
        "Revenues": "Total Net Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax": "Transaction-based Revenues",  # Verify
        "InterestIncomeExpenseNet": "Net Interest Revenues",
        "OtherOperatingIncome": "Other Revenues",  # Adjust from OtherNonoperatingIncomeExpense
        "FloorBrokerageExchangeAndClearanceFees": "Brokerage and Transaction",
        "ResearchAndDevelopmentExpense": "Technology and Development",  # Needs adjustment
        "MarketingExpense": "Marketing",
        "GeneralAndAdministrativeExpense": "General and Administrative",
        "OperatingExpenses": "Total Operating Expenses",
        "GainLossOnSaleOfDerivatives": "Change in Fair Value of Convertible Notes",  # Adjust
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
                # Relax year filter to catch historical data (e.g., 2020 in 2021 10-K)
                if year and 2020 <= year <= 2024 and entry.get("form") == "10-K":
                    income_data[label][year] = entry["val"] / 1_000_000

#trying for specific expenses. 
    if "Total Operating Expenses" in income_data:
        for year in income_data["Total Operating Expenses"]:
            total_op_exp = income_data["Total Operating Expenses"].get(year, 0)
            brokerage = income_data["Brokerage and Transaction"].get(year, 0)
            tech_dev = income_data["Technology and Development"].get(year, 0)
            marketing = income_data["Marketing"].get(year, 0)
            g_and_a = income_data["General and Administrative"].get(year, 0)
            operations = total_op_exp - (brokerage + tech_dev + marketing + g_and_a)
            # Only add if positive to avoid errors
            if operations >= 0:
                income_data.setdefault("Operations", {})[year] = operations
    
    return income_data

#creating rows and cols. 
def create_dataframe(income_data):
    # Get all unique years and sort them
    years = sorted(set().union(*[set(d.keys()) for d in income_data.values()]))
    
    # Build the DataFrame with items as rows and years as columns
    df_data = {}
    for label in income_data:
        df_data[label] = [income_data[label].get(year, None) for year in years]
    
    # Create DataFrame with items as rows
    df = pd.DataFrame(df_data, index=years)
    
    # Transpose to get years as columns
    df = df.transpose()
    
    # Reset index to make the items a column
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Item'}, inplace=True)
    
    return df
#saving information to csv 
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
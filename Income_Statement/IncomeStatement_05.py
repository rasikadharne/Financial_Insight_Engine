#Removed some of the not required tags and formulas/calculations to get to the tag
import requests
import pandas as pd

CIK = "0001783879"  # Robinhood Markets, Inc.
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
        # Revenue Section
        "Revenues": ("Total Net Revenues", "USD"),
        # Operating Expense Section
        "FloorBrokerageExchangeAndClearanceFees": ("Brokerage and Transaction", "USD"),
        "ResearchAndDevelopmentExpense": ("ResearchAndDevelopmentExpense", "USD"),
        "AllocatedShareBasedCompensationExpense": ("Employee Stock Pay Cost", "USD"),
        "AmortizationOfIntangibleAssets": ("AmortizationOfIntangibleAssets", "USD"),
        "CapitalizedComputerSoftwareAmortization1": ("Software Cost", "USD"),
        "ContractWithCustomerAssetCreditLossExpense": ("ContractWithCustomerAssetCreditLossExpense", "USD"),
        "MarketingExpense": ("Marketing", "USD"),
        "GeneralAndAdministrativeExpense": ("General and Administrative", "USD"),
        "OperatingExpenses": ("Total Operating Expenses", "USD"),
        "Depreciation": ("Depreciation", "USD"),        
        "DepreciationDepletionAndAmortization": ("DepreciationDepletionAndAmortization", "USD"), 
        "OtherCostAndExpenseOperating": ("Other Expenses", "USD"), 
        "ProvisionForDoubtfulAccounts": ("ProvisionForDoubtfulAccounts Expenses", "USD"), 
        "ShareBasedCompensation": ("ShareBasedCompensation Expenses", "USD"), 
        "ShortTermLeaseCost": ("ShortTermLeaseCost", "USD"), 
        "AdvertisingExpense": ("Advertising Expense", "USD"), 
        # Net Income
        "NetIncomeLoss": ("Net Income (Loss)", "USD"),
        "NetIncomeLossAvailableToCommonStockholdersBasic": ("Net Income (Loss) Attributable to Common Stockholders (Basic)", "USD"),
        "NetIncomeLossAvailableToCommonStockholdersDiluted": ("Net Income (Loss) Attributable to Common Stockholders (Diluted)", "USD"),
        # Interest Expense
        "InterestExpenseBorrowings": ("Interest Expense", "USD"), 
        "InterestIncomeExpenseNet": ("Interest Expense Net", "USD"), 
        # Non-Operating Income/Expense
        "OtherNonoperatingIncomeExpense": ("OtherNonoperatingIncomeExpense", "USD"), 
        # Income Tax Benefits
        "CurrentIncomeTaxExpenseBenefit": ("Total income tax benefit", "USD"), 
        "CurrentFederalTaxExpenseBenefit": ("Federal income tax benefit", "USD"), 
        "CurrentForeignTaxExpenseBenefit": ("Foreign income tax benefit", "USD"), 
        "CurrentStateAndLocalTaxExpenseBenefit": ("State income tax benefit", "USD"), 
        # Income (Loss) Before Income Tax
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments": ("Income Before Equity Investments, Taxes, and Noncontrolling Interest", "USD"), 
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": ("Income before tax from cont operation", "USD"), 
        # Income Tax Expense Section
        "DeferredIncomeTaxExpenseBenefit": ("DeferredIncomeTaxExpenseBenefit", "USD"),
        "IncomeTaxExpenseBenefit": ("Provision for Income Taxes", "USD"),
        # Other Section
        "EarningsPerShareBasic": ("Net Income (Loss) Per Share (Basic)", "pure"),
        "EarningsPerShareDiluted": ("Net Income (Loss) Per Share (Diluted)", "pure"),
        "WeightedAverageNumberOfSharesOutstandingBasic": ("Weighted-Average Shares (Basic)", "shares"),
        "WeightedAverageNumberOfDilutedSharesOutstanding": ("Weighted-Average Shares (Diluted)", "shares")
    }
    
    # Initialize dictionary with labels as keys
    income_data = {label: {} for label, _ in income_tags.values()}
    
    # Extract data for each tag
    for tag, (label, unit) in income_tags.items():
        if tag in xbrl_data:
            units = xbrl_data[tag]["units"]
            if unit in units:
                entries = units[unit]
                print(f"Tag: {tag}, Label: {label}, Entries for {unit}:")
                for entry in entries:
                    year = entry.get("fy")
                    form = entry.get("form")
                    if year and 2020 <= year <= 2024 and form == "10-K":
                        value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]
                        print(f"  Year: {year}, Form: {form}, Value: {value}")
                        income_data[label][year] = value
            else:
                print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
        else:
            print(f"Tag {tag} not found in XBRL data.")
    
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
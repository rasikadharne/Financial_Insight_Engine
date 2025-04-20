#Version 01 had placeholder tags, removing them 
#also assets was not pulling in v1 tryiung to fix the same here in v2
#fixed minor bugs in XBRL tags 

import requests
import pandas as pd

CIK = "0001783879"  # Robinhood Markets, Inc.
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "your-email@example.com"}  # Replace with your email

def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def extract_balance_sheet_data(xbrl_data):
    balance_sheet_tags = {
        # Current Assets
        "CashAndCashEquivalentsAtCarryingValue": ("Cash and cash equivalents", "USD", "Current Asset"),
        "CashAndSecuritiesSegregatedUnderSecuritiesExchangeCommissionRegulation": (
            "Cash segregated under federal and other regulations", "USD", "Current Asset"),
        "ReceivablesFromBrokersDealersAndClearingOrganizations": (
            "Receivables from brokers, dealers, and clearing organizations", "USD", "Current Asset"),
        "ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent": (
            "Receivables from users, net", "USD", "Current Asset"),
        "SecuritiesBorrowed": ("Securities borrowed", "USD", "Current Asset"),
        "DepositsWithClearingOrganizationsAndOthersSecurities": (
            "Deposits with clearing organizations", "USD", "Current Asset"),
        "SafeguardingAssetPlatformOperatorCryptoAsset": (
            "Asset related to user cryptocurrencies safeguarding obligation", "USD", "Current Asset"),
        "PrepaidExpenseCurrent": ("Prepaid expenses", "USD", "Current Asset"),
        "AssetsCurrent": ("Total current assets", "USD", "Current Asset"),

        # Property
        "PropertyPlantAndEquipmentNet": ("Property, software, and equipment, net", "USD", "Property"),

        # Goodwill
        "Goodwill": ("Goodwill", "USD", "Goodwill"),

        # Intangible Assets
        "IntangibleAssetsNetExcludingGoodwill": ("Intangible assets, net", "USD", "Intangible Assets"),

        # Non-Current Assets
        "PrepaidExpenseNoncurrent": ("Non-current prepaid expenses", "USD", "Non-Current Assets"),
        "OtherAssetsNoncurrent": ("Other non-current assets", "USD", "Non-Current Assets"),

        # Total Assets
        "Assets": ("Total assets", "USD", "Total Assets"),

        # Current Liabilities
        "AccountsPayableAndAccruedLiabilitiesCurrent": (
            "Accounts payable and accrued expenses", "USD", "Liability & Stock Equity - Current Liabilities"),
        "ContractWithCustomerLiabilityCurrent": (
            "Payables to users", "USD", "Liability & Stock Equity - Current Liabilities"),
        "SecuritiesLoaned": ("Securities loaned", "USD", "Liability & Stock Equity - Current Liabilities"),
        "SafeguardingAssetPlatformOperatorCryptoAsset": (
            "User cryptocurrencies safeguarding obligation", "USD", "Liability & Stock Equity - Current Liabilities"),
        # Placeholder tags (commented out as they may not exist)
        # "FractionalSharesRepurchaseObligation": (
        #     "Fractional shares repurchase obligation", "USD", "Liability & Stock Equity - Current Liabilities"),
        # "OtherCurrentLiabilities": (
        #     "Other current liabilities", "USD", "Liability & Stock Equity - Current Liabilities"),
        "LiabilitiesCurrent": (
            "Total current liabilities", "USD", "Liability & Stock Equity - Current Liabilities"),

        # Non-Current Liabilities
        # "OtherNonCurrentLiabilities": (
        #     "Other non-current liabilities", "USD", "Liability & Stock Equity - Non-Current Liabilities"),

        # Total Liabilities
        "Liabilities": ("Total liabilities", "USD", "Liability & Stock Equity - Total Liabilities"),

        # Equity
        "AdditionalPaidInCapital": ("Additional paid-in capital", "USD", "Equity"),
        "RetainedEarningsAccumulatedDeficit": ("Accumulated deficit", "USD", "Equity"),
        "StockholdersEquity": ("Total stockholders’ equity", "USD", "Equity"),

        # Total Liabilities and Stockholders’ Equity
        "LiabilitiesAndStockholdersEquity": (
            "Total liabilities and stockholders’ equity", "USD", "Total Liabilities and Stockholders’ Equity"),
    }

    balance_sheet_data = {
        "Current Asset": {},
        "Property": {},
        "Goodwill": {},
        "Intangible Assets": {},
        "Non-Current Assets": {},
        "Total Assets": {},
        "Liability & Stock Equity - Current Liabilities": {},
        "Liability & Stock Equity - Non-Current Liabilities": {},
        "Liability & Stock Equity - Total Liabilities": {},
        "Equity": {},
        "Total Liabilities and Stockholders’ Equity": {},  # Added missing category
    }

    # Extract data for each tag
    for tag, (label, unit, category) in balance_sheet_tags.items():
        if tag in xbrl_data:
            units = xbrl_data[tag]["units"]
            if unit in units:
                entries = units[unit]
                print(f"Tag: {tag}, Label: {label}, Category: {category}, Entries for {unit}:")
                if label not in balance_sheet_data[category]:
                    balance_sheet_data[category][label] = {}
                for entry in entries:
                    year = entry.get("fy")
                    form = entry.get("form")
                    if year and 2020 <= year <= 2024 and form == "10-K":
                        value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]
                        print(f"  Year: {year}, Form: {form}, Value: {value} million")
                        balance_sheet_data[category][label][year] = value
            else:
                print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
        else:
            print(f"Tag {tag} not found in XBRL data.")

    return balance_sheet_data

def create_dataframe(balance_data):
    # Collect all unique years across all categories and items
    years = set()
    for category, items in balance_data.items():
        for label, year_data in items.items():
            years.update(year_data.keys())
    years = sorted(years)  # Sort years in ascending order

    category_order = [
        "Current Asset",
        "Property",
        "Goodwill",
        "Intangible Assets",
        "Non-Current Assets",
        "Total Assets",
        "Liability & Stock Equity - Current Liabilities",
        "Liability & Stock Equity - Non-Current Liabilities",
        "Liability & Stock Equity - Total Liabilities",
        "Equity",
        "Total Liabilities and Stockholders’ Equity",
    ]
    dfs = []

    # Build a sub-DataFrame for each category
    for category in category_order:
        if category in balance_data and balance_data[category]:  # Check if category has data
            # Create a section header row
            header_row = pd.DataFrame([[f"**{category}**", ""] + [None] * len(years)], columns=["Category", "Item"] + years)

            # Build data for items in this category
            category_data = []
            for label in sorted(balance_data[category].keys()):  # Sort labels alphabetically
                row = [label] + [balance_data[category][label].get(year, None) for year in years]
                category_data.append(row)

            # Create a sub-DataFrame for the items in this category
            category_df = pd.DataFrame(category_data, columns=["Item"] + years)

            # Concatenate the header and the category items
            dfs.extend([header_row, category_df])

    # Concatenate all sub-DataFrames vertically
    if dfs:  # Check if dfs is not empty
        final_df = pd.concat(dfs, ignore_index=True)
    else:
        # Return an empty DataFrame with correct columns if no data
        final_df = pd.DataFrame(columns=["Category", "Item"] + years)

    return final_df

def save_to_csv(df, filename="robinhood_balance_sheet.csv"):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    xbrl_data = get_xbrl_data()
    balance_data = extract_balance_sheet_data(xbrl_data)
    print("\nExtracted Balance Sheet Data (2020-2024, 10-K only, in millions):")
    for category, items in balance_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")

    df = create_dataframe(balance_data)
    print("\nDataFrame:")
    print(df)
    save_to_csv(df)
#Fixing minor bugs wqhich do not present data right
#Some of the tags are not correctly consolidated under right category, this version fixes that 
#pullling more tags that can be used universally 

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
        # Total Assets
        "Assets": ("Total assets", "USD", "Total Assets"),
        # Current Assets
        "AssetsCurrent": ("Total current assets", "USD", "Current Asset"),
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
        "ReceivablesFromCustomersNet": ("Receivable from users Net", "USD", "Current Asset"),
        "SecuritiesBorrowed": ("Securities borrowed", "USD", "Current Asset"),
        "DerivativeAssetsCurrent": ("Derivative assets current", "USD", "Current Asset"),
        "LoansAndLeasesReceivableCurrent": ("Loans and leases receivable current", "USD", "Current Asset"),
        "MarketableSecuritiesCurrent": ("Marketable Securities Current", "USD", "Current Asset"),
        "OtherAssetsCurrent": ("Other Assets Current", "USD", "Current Asset"),
        "AccountsReceivableNetCurrent": ("Accounts Receivable Net Current", "USD", "Current Asset"),
        "InventoryNet": ("Inventory Net", "USD", "Current Asset"),
        "DeferredTaxAssetsCurrent": ("Deferred Tax Assets Current", "USD", "Current Asset"),
        "OtherReceivablesCurrent": ("Other Receivables Current", "USD", "Current Asset"),
        # Non-Current Assets
        "AssetsNoncurrent": ("Total Non-Current Assets", "USD", "Non-Current Assets"),
        "PropertyPlantAndEquipmentNet": ("Property, software, and equipment, net", "USD", "Non-Current Assets"),
        "Goodwill": ("Goodwill", "USD", "Non-Current Assets"),
        "IntangibleAssetsNetExcludingGoodwill": ("Intangible assets, net", "USD", "Non-Current Assets"),
        "PrepaidExpenseNoncurrent": ("Non-current prepaid expenses", "USD", "Non-Current Assets"),
        "OtherAssetsNoncurrent": ("Other non-current assets", "USD", "Non-Current Assets"),
        "OperatingLeaseRightOfUseAssetNoncurrent": (
        "Operating Lease Right-of-Use Assets", "USD", "Non-Current Assets"),
        "FinanceLeaseRightOfUseAssetNoncurrent": ("Finance Lease Right-of-Use Assets", "USD", "Non-Current Assets"),
        "InvestmentsEquitySecurities": ("Investments Equity Securities", "USD", "Non-Current Assets"),
        "DeferredTaxAssetsNoncurrent": ("Deferred Tax Assets Noncurrent", "USD", "Non-Current Assets"),
        "LongTermInvestments": ("LongTermInvestments", "USD", "Non-Current Assets"),
        "RestrictedCashAndCashEquivalentsNoncurrent": ("Restricted Cash Noncurrent", "USD", "Non-Current Assets"),
        "NotesReceivableNoncurrent": ("NotesReceivableNoncurrent", "USD", "Non-Current Assets"),
        # Total Liabilities
        "Liabilities": ("Total liabilities", "USD", "Liability & Stock Equity - Total Liabilities"),
        # Current Liabilities
        "LiabilitiesCurrent": (
        "Total current liabilities", "USD", "Liability & Stock Equity - Current Liabilities"),
        "AccountsPayableAndAccruedLiabilitiesCurrent": (
        "Accounts payable and accrued expenses", "USD", "Liability & Stock Equity - Current Liabilities"),
        "ContractWithCustomerLiabilityCurrent": (
        "Payables to users", "USD", "Liability & Stock Equity - Current Liabilities"),
        "SecuritiesLoaned": ("Securities loaned", "USD", "Liability & Stock Equity - Current Liabilities"),
        "SafeguardingAssetPlatformOperatorCryptoAsset": (
        "User cryptocurrencies safeguarding obligation", "USD", "Liability & Stock Equity - Current Liabilities"),
        "OtherCurrentLiabilities": ("Other current liabilities", "USD", "Liability & Stock Equity - Current Liabilities"),
        "AccruedLiabilitiesCurrent": (
        "Accrued Liabilities Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "AccountsPayableCurrent": (
        "Accounts Payable Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "DeferredRevenueCurrent": (
        "Deferred Revenue Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "TaxesPayableCurrent": (
        "Incometax Payable Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "OperatingLeaseLiabilityCurrent": (
        "Operating LeaseLiability Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "FinanceLeaseLiabilityCurrent": (
        "Finance Lease Liability Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "CustomerDepositLiabilityCurrent": (
        "Customer Deposit Liability Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "DividendsPayable": ("Dividends Payable", "USD", "Liability & Stock Equity - Current Liabilities"),
        "InterestPayableCurrent": (
        "Interest Payable Current", "USD", "Liability & Stock Equity - Current Liabilities"),
        "OtherCurrentLiabilities": (
        "Other Current Liabilitiest", "USD", "Liability & Stock Equity - Current Liabilities"),
        # Non-Current Liabilities
        "LiabilitiesNoncurrent": (
        "LiabilitiesNoncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "OtherNonCurrentLiabilities": (
        "Other non-current liabilities", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "LongTermDebtNoncurrent": (
        "Long Term Debt Noncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "DeferredRevenueNoncurrent": (
        "Deferred Revenue Noncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "OperatingLeaseLiabilityNoncurrent": (
        "Operating Lease Liability Noncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "FinanceLeaseLiabilityNoncurrent": (
        "Finance Lease Liability Noncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "DeferredTaxLiabilitiesNoncurrent": (
        "DeferredTaxLiabilitiesNoncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "AccruedLiabilitiesNoncurrent": (
        "AccruedLiabilitiesNoncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "CustomerDepositLiabilityNoncurrent": (
        "CustomerDepositLiabilityNoncurrent", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        "AssetRetirementObligation": (
        "AssetRetirementObligation", "USD", "Liability & Stock Equity - Non-Current Liabilities"),
        # Equity
        "AdditionalPaidInCapital": ("Additional paid-in capital", "USD", "Equity"),
        "RetainedEarningsAccumulatedDeficit": ("Accumulated deficit", "USD", "Equity"),
        "StockholdersEquity": ("Total stockholders equity", "USD", "Equity"),
        "CommonStockValue": ("Common Stock Value", "USD", "Equity"),
        "PreferredStockValue": ("Preferred Stock Value", "USD", "Equity"),
        "TreasuryStockValue": ("Treasury Stock Value", "USD", "Equity"),
        "AccumulatedOtherComprehensiveIncomeLoss": (
        "Accumulated Other ComprehensiveIncomeLoss", "USD", "Equity"),
        "CommonStockSharesIssued": ("Common Stock Shares Issued", "shares", "Equity"),
        "CommonStockSharesOutstanding": ("Common Stock Shares Outstanding", "shares", "Equity"),
        "NoncontrollingInterest": ("Non controlling Interest", "USD", "Equity"),
        # Total Liabilities and Stockholders’ Equity
        "LiabilitiesAndStockholdersEquity": (
        "Total liabilities and stockholders equity", "USD", "Total Liabilities and Stockholders’ Equity"),
    }

    balance_sheet_data = {
        "Current Asset": {},
        "Non-Current Assets": {},
        "Total Assets": {},
        "Liability & Stock Equity - Current Liabilities": {},
        "Liability & Stock Equity - Non-Current Liabilities": {},
        "Liability & Stock Equity - Total Liabilities": {},
        "Equity": {},
        "Total Liabilities and Stockholders’ Equity": {},
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
                        # Handle different units: USD in millions, shares in whole numbers
                        if unit == "USD":
                            value = entry["val"] / 1_000_000  # Convert USD to millions
                        elif unit == "shares":
                            value = entry["val"] / 1_000_000 # in million shares
                        else:
                            value = entry["val"]  # Default: no scaling
                
                        print(f"  Year: {year}, Form: {form}, Value: {value}")
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
        "Total Assets",
        "Current Asset",
        "Non-Current Assets",
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
    print("\nExtracted Balance Sheet Data (2020-2024, 10-K only):")
    for category, items in balance_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")

    df = create_dataframe(balance_data)
    print("\nDataFrame:")
    print(df)
    save_to_csv(df)
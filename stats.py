import pandas as pd
from bs4 import BeautifulSoup

# 1. Configuration & Exchange Rates (Jan 10, 2026)
EXCHANGE_RATES = {
    'USD': 1.0,   'EUR': 1.163, 'GBP': 1.341,
    'AUD': 0.670, 'CAD': 0.718, 'PLN': 0.276,
    'CHF': 1.249, 'UAH': 0.023
}

def clean_amount(amount_str):
    # Remove commas and non-numeric characters except decimals
    clean_str = "".join(c for c in amount_str if c.isdigit() or c == '.')
    return float(clean_str) if clean_str else 0.0

# 2. Parse HTML
with open('2.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

all_divs = soup.find_all('div', class_='rounded-full')
data_rows = []

for div in all_divs:
    text = div.get_text(strip=True)
    if any(curr in text for curr in EXCHANGE_RATES.keys()):
        card = div.find_parent('div', class_='border')
        if not card: continue

        # Normalization logic
        amount_usd = 0.0
        if " " in text:
            currency, amt_str = text.split(" ", 1)
            amount_usd = round(clean_amount(amt_str) * EXCHANGE_RATES.get(currency, 1.0), 2)

        name_el = card.find('div', class_='font-semibold')
        donor = name_el.get_text(strip=True) if name_el and name_el.get_text(strip=True) else "Anonymous"
        
        battalion_el = card.find('div', class_='bg-gray-800')
        battalion = battalion_el.get_text(strip=True) if battalion_el else "Unassigned"

        data_rows.append({
            'Date': card.find('div', class_='text-neutral-400').get_text(strip=True) if card.find('div', class_='text-neutral-400') else "Unknown",
            'Donor': donor,
            'Battalion': battalion,
            'Amount_USD': amount_usd
        })

# 3. Data Processing & Summary Generation
df = pd.DataFrame(data_rows)
df.to_csv('normalized_donations.csv', index=False)

# Battalion Stats (Total, Count, Average)
battalion_stats = df.groupby('Battalion')['Amount_USD'].agg(['sum', 'count', 'mean']).reset_index()
battalion_stats.columns = ['Battalion', 'Total_USD', 'Donation_Count', 'Average_USD']
battalion_stats = battalion_stats.sort_values(by='Total_USD', ascending=False)
battalion_stats.to_csv('battalion_stats.csv', index=False)

# Top 10 Donors across all battalions
top_donors = df.groupby('Donor')['Amount_USD'].sum().nlargest(10).reset_index()
top_donors.to_csv('top_10_donors.csv', index=False)

print("--- TOP 10 DONORS (USD) ---")
print(top_donors.to_string(index=False))

print("\n--- BATTALION SUMMARY (USD) ---")
pd.options.display.float_format = '{:,.2f}'.format
print(battalion_stats.to_string(index=False))
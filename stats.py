import pandas as pd
from bs4 import BeautifulSoup

# 1. Configuration & Exchange Rates
EXCHANGE_RATES = {
    'USD': 1.0,   'EUR': 1.163, 'GBP': 1.341,
    'AUD': 0.670, 'CAD': 0.718, 'PLN': 0.276,
    'CHF': 1.249, 'UAH': 0.023
}

def clean_amount(amount_str):
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

        # Amount Normalization
        amount_usd = 0.0
        if " " in text:
            currency, amt_str = text.split(" ", 1)
            amount_usd = round(clean_amount(amt_str) * EXCHANGE_RATES.get(currency, 1.0), 2)

        name_el = card.find('div', class_='font-semibold')
        donor = name_el.get_text(strip=True) if name_el and name_el.get_text(strip=True) else "Anonymous"
        battalion_el = card.find('div', class_='bg-gray-800')
        battalion = battalion_el.get_text(strip=True) if battalion_el else "Unassigned"
        date_el = card.find('div', class_='text-neutral-400')
        date_str = date_el.get_text(strip=True) if date_el else "01/01/70"

        data_rows.append({
            'Date': date_str,
            'Donor': donor,
            'Battalion': battalion,
            'Amount_USD': amount_usd
        })

# 3. Data Cleaning and Sorting
df = pd.DataFrame(data_rows)

# Convert Date to actual datetime objects for accurate sorting
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y', errors='coerce')

# Remove identical duplicates (entries with same Donor, Date, Battalion, and Amount)
initial_count = len(df)
df = df.drop_duplicates()
removed_count = initial_count - len(df)

# Sort by Date descending (Newest first)
df = df.sort_values(by='Date', ascending=False)

# Convert Date back to string format for the final CSV
df['Date'] = df['Date'].dt.strftime('%m/%d/%y')

# 4. Generate Reports
df.to_csv('normalized_donations.csv', index=False)

# Battalion Stats
battalion_stats = df.groupby('Battalion')['Amount_USD'].agg(['sum', 'count', 'mean']).reset_index()
battalion_stats.columns = ['Battalion', 'Total_USD', 'Donation_Count', 'Average_USD']
battalion_stats = battalion_stats.sort_values(by='Total_USD', ascending=False)
battalion_stats.to_csv('battalion_stats.csv', index=False)

# Top 10 Donors
top_donors = df.groupby('Donor')['Amount_USD'].sum().nlargest(10).reset_index()
top_donors.to_csv('top_10_donors.csv', index=False)

print(f"Removed {removed_count} duplicate entries.")
print(f"Final unique donation count: {len(df)}")
print("\n--- NEWEST 5 DONATIONS ---")
print(df.head(5).to_string(index=False))

print("\n--- TOP 10 DONORS ---")
print(top_donors.to_string(index=False))
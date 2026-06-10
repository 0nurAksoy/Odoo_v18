# TCMB Currency Sync — Odoo 18

![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)

Automatically fetches live **USD** and **EUR** exchange rates from the **Turkish Central Bank (TCMB)** and syncs them into Odoo 18 every hour.

## Why?
Turkish businesses using Odoo need accurate daily exchange rates for sales orders, invoices, and reports. This module eliminates manual rate entry by pulling directly from Turkey's official central bank API.

## Features
- Fetches official USD/EUR rates from [TCMB](https://www.tcmb.gov.tr)
- Syncs automatically every hour via Odoo's built-in scheduler
- Updates existing rates instead of creating duplicates
- Zero configuration needed after installation

## Compatibility
| | |
|---|---|
| **Odoo Version** | 18.0 Community & Enterprise |
| **Deployment** | On-Premise |
| **Dependencies** | `base`, `account` |

## Installation

**Option 1 — Manual**
1. Copy the `tcmb_currency_sync` folder into your Odoo `custom-addons` directory
2. Restart Odoo:
```bash
   sudo systemctl restart odoo
```
3. Go to **Apps → Update Apps List**
4. Search for **TCMB** and click **Install**

**Option 2 — Git Clone**
```bash
cd /your/custom-addons/path
git clone https://github.com/0nurAksoy/tcmb_currency_sync.git
sudo systemctl restart odoo
```

## How it works

ir.cron (every hour)
→ fetches XML from tcmb.gov.tr
→ parses USD and EUR ForexBuying rates
→ updates res.currency.rate in Odoo

## Verify Rates

Accounting → Configuration → Currencies → USD or EUR → Rates tab

## Author
**Onur Aksoy**
GitHub: [@0nurAksoy](https://github.com/0nurAksoy)

## License
LGPL-3

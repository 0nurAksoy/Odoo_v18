# TCMB Currency Sync — Odoo 18

![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Status](https://img.shields.io/badge/Status-MVP-orange)

TCMB Currency Sync is a custom Odoo 18 addon that fetches official daily USD and EUR exchange rates from the Central Bank of the Republic of Türkiye (TCMB) and synchronizes them into Odoo currency rates.

This addon is designed as a practical Odoo backend development project focused on scheduled actions, external XML data integration, and accounting-related currency rate updates.

---

## Why?

Companies using Odoo in Türkiye may need to keep exchange rates up to date for accounting, sales, purchases, invoices, and reporting.

This module reduces manual currency rate entry by fetching official daily exchange rate data from TCMB and updating the related Odoo currency rate records automatically.

---

## Features

- Fetches official daily USD and EUR exchange rates from TCMB
- Uses TCMB `ForexBuying` as the selected source rate
- Runs automatically once per day using Odoo Scheduled Actions (`ir.cron`)
- Creates or updates Odoo currency rate records for the current date
- Uses Odoo's native `res.currency` and `res.currency.rate` models
- Designed for Odoo 18 local/on-premise development environments
- Requires minimal configuration after installation

---

## Compatibility

| Item | Value |
|---|---|
| Odoo Version | 18.0 |
| Edition | Community / Enterprise |
| Deployment | Local / On-premise |
| Operating System | Ubuntu/Linux recommended |
| Dependencies | `base`, `account` |
| Python Dependency | `requests` |
| License | LGPL-3 |

---

## Design Decision

TCMB provides multiple exchange rate types, including:

- Forex Buying
- Forex Selling
- Banknote Buying
- Banknote Selling

The first version of this addon uses `ForexBuying` as the selected source rate.

This was a deliberate MVP decision because Odoo currency rate records are updated with a single rate value for a currency/date scenario. Future versions may include a configuration option to choose which TCMB rate type should be used.

---

## Repository Structure

This addon is part of an Odoo 18 addon collection repository.

```text
Odoo_v18/
└── tcmb_currency_sync/
    ├── data/
    │   └── cron.xml
    ├── models/
    │   ├── __init__.py
    │   └── currency_sync.py
    ├── static/
    │   └── description/
    ├── __init__.py
    ├── __manifest__.py
    ├── .gitignore
    └── README.md
```

---

## Installation

There are two recommended installation options.

### Option 1 — Use the repository as an addons path

This is the recommended option if you want to keep multiple Odoo 18 addons inside the same repository.

1. Clone the repository:

```bash
cd /opt/odoo/custom-src
git clone https://github.com/0nurAksoy/Odoo_v18.git
```

2. Add the repository path to your `addons_path` in `odoo.conf`:

```ini
addons_path = /path/to/odoo/addons,/opt/odoo/custom-src/Odoo_v18
```

3. Restart Odoo:

```bash
sudo systemctl restart odoo
```

4. Activate Developer Mode in Odoo.

5. Go to:

```text
Apps → Update Apps List
```

6. Search for:

```text
TCMB Currency Sync
```

7. Install the module.

---

### Option 2 — Copy only the addon folder

Use this option if you want to install only this addon into an existing custom addons directory.

1. Clone the repository:

```bash
git clone https://github.com/0nurAksoy/Odoo_v18.git
```

2. Copy the addon folder into your custom addons directory:

```bash
cp -r Odoo_v18/tcmb_currency_sync /path/to/your/custom-addons/
```

3. Make sure your custom addons directory exists in `odoo.conf`:

```ini
addons_path = /path/to/odoo/addons,/path/to/your/custom-addons
```

4. Restart Odoo:

```bash
sudo systemctl restart odoo
```

5. Update the Apps list and install the module.

---

## Important Git Clone Note

Do not clone the GitHub subfolder URL directly.

This is not a valid addon clone command:

```bash
git clone https://github.com/0nurAksoy/Odoo_v18/tree/main/tcmb_currency_sync
```

Git clones repositories, not GitHub web subfolder URLs.

Use this instead:

```bash
git clone https://github.com/0nurAksoy/Odoo_v18.git
```

Then either add the repository to `addons_path` or copy the `tcmb_currency_sync` folder into your custom addons directory.

---

## Configuration

After installation:

1. Make sure the Accounting module is available.
2. Make sure USD and EUR currencies exist in Odoo.
3. Make sure USD and EUR are active if you want to see and use their rates.
4. Update the Apps list after adding the addon to your addons path.
5. Install `TCMB Currency Sync`.

If the module does not appear in the Apps menu:

- Check your `addons_path`
- Restart Odoo
- Update the Apps list
- Remove the default "Apps" filter if necessary
- Search for `TCMB` or `TCMB Currency Sync`

---

## How It Works

The synchronization flow is:

```text
Scheduled Action
      ↓
Fetch TCMB daily XML data
      ↓
Parse USD and EUR ForexBuying values
      ↓
Find matching currencies in Odoo
      ↓
Create or update res.currency.rate records
```

More specifically:

1. Odoo runs the scheduled action once per day.
2. The addon sends a request to TCMB's daily XML exchange rate source.
3. It parses the XML response.
4. It extracts `ForexBuying` values for USD and EUR.
5. It searches for matching `res.currency` records in Odoo.
6. It creates or updates the related `res.currency.rate` records for the current date.

---

## Scheduled Action

The module creates an Odoo scheduled action using `ir.cron`.

Default behavior:

| Field | Value |
|---|---|
| Frequency | Once per day |
| Model | `tcmb.currency.sync` |
| Method | `sync_rates()` |
| Purpose | Fetch and update TCMB exchange rates |

You can review the scheduled action from Developer Mode:

```text
Settings → Technical → Automation → Scheduled Actions
```

Search for:

```text
TCMB Currency Sync
```

Depending on your Odoo configuration, you may also run the scheduled action manually from this screen.

---

## Verify Rates

After installation and synchronization, you can verify the updated rates from:

```text
Accounting → Configuration → Currencies
```

Then open USD or EUR and check the Rates tab.

You can also check the `res.currency.rate` records from Developer Mode if needed.

---

## Manual QA Checklist

Use this checklist to verify the module in a local Odoo 18 environment:

1. Add the addon to a valid `addons_path`.
2. Restart Odoo.
3. Update the Apps list.
4. Install `TCMB Currency Sync`.
5. Confirm that the scheduled action was created.
6. Run the scheduled action manually or wait for its next execution.
7. Open USD and EUR currencies.
8. Check whether a rate record exists for the current date.
9. Run the scheduled action again and confirm that it updates the existing rate instead of creating duplicate records.
10. Check Odoo logs if the TCMB request fails.

---

## Limitations

This is the first MVP version of the addon.

Current limitations:

- Supports USD and EUR only
- Uses TCMB `ForexBuying` rate only
- Does not yet provide a configuration screen
- Error handling can be improved
- Automated tests are not included yet
- Multi-company behavior should be reviewed before production use
- Historical rate synchronization is not implemented yet

---

## Roadmap

Planned improvements:

- Add configurable currency selection
- Add configurable TCMB rate type selection:
  - Forex Buying
  - Forex Selling
  - Banknote Buying
  - Banknote Selling
- Improve logging and error handling
- Add multi-company support
- Add historical rate synchronization
- Add automated tests
- Add screenshots and usage examples
- Improve installation documentation based on real deployment feedback

---

## Developer Notes

The addon currently uses Python's `requests` package to fetch TCMB XML data.

If `requests` is not available in your Odoo environment, install it with:

```bash
pip install requests
```

For production-like environments, it is recommended to declare this dependency in the module manifest using `external_dependencies`.

Example:

```python
'external_dependencies': {
    'python': ['requests'],
},
```

---

## Troubleshooting

### The module does not appear in Apps

Check the following:

- The addon path is correctly added to `odoo.conf`
- Odoo was restarted after changing `addons_path`
- The Apps list was updated
- The default Apps filter was removed
- The folder contains a valid `__manifest__.py` file

### Rates are not updated

Check the following:

- USD and EUR currencies exist in Odoo
- USD and EUR currencies are active
- The scheduled action is active
- Odoo can access TCMB's XML source
- The server has internet access
- Odoo logs do not show request or XML parsing errors

### Duplicate rates are created

The module is designed to update an existing rate for the same currency and date. If duplicates appear, review:

- Existing `res.currency.rate` records
- Company-specific currency rate behavior
- Multi-company configuration
- The search domain used before creating a new rate

---

## Status

This addon is currently an MVP / portfolio project.

It is suitable for learning, demonstration, and local Odoo 18 development practice. Before using it in a production environment, review security, error handling, multi-company behavior, logging, and automated test coverage.

---

## Author

**Onur Aksoy**

GitHub: [@0nurAksoy](https://github.com/0nurAksoy)

---

## License

LGPL-3
# oa_stock_age — Stock Age Report

## Overview

This module identifies slow-moving inventory by calculating how long
each product has been sitting in stock at each warehouse location.

It helps inventory managers make better purchasing and pricing decisions
by surfacing products that have not moved for a long time.

## Features

- Shows age in days for all products currently in stock (qty > 0)
- Age is defined as: today minus the date of the oldest incoming
  stock move for quantities still on hand
- Organized per product and location combination
- Filter by products older than 90 or 180 days
- Group by location or product
- Data is refreshed automatically via a daily scheduled action
- Accessible at: Inventory → Reporting → Stock Age Report

## Technical Details

| Item            | Value                        |
|-----------------|------------------------------|
| Odoo Version    | 18.0                         |
| Author          | Onur Aksoy                   |
| License         | LGPL-3                       |
| Dependencies    | stock                        |
| Custom Model    | stock.age.report             |

## Installation

1. Copy `oa_stock_age` into your custom addons directory.
2. Restart the Odoo server.
3. Enable developer mode.
4. Go to Apps → Update Apps List.
5. Search for "Stock Age Report" and install.

## Configuration

The scheduled action **Stock Age Report: Daily Refresh** runs
automatically every day at 06:00.

To trigger a manual refresh:
- Go to Settings → Technical → Scheduled Actions
- Find "Stock Age Report: Daily Refresh"
- Click Run Manually

## Data Model

**Model:** `stock.age.report`

| Field             | Type       | Description                          |
|-------------------|------------|--------------------------------------|
| product_id        | Many2one   | Product                              |
| location_id       | Many2one   | Internal warehouse location          |
| qty_on_hand       | Float      | Current quantity in stock            |
| oldest_move_date  | Date       | Date of oldest incoming stock move   |
| age_days          | Integer    | Days since oldest incoming move      |
| last_refresh      | Datetime   | Timestamp of last data refresh       |

## Known Limitations

- Age is calculated from the oldest incoming move, not FIFO cost layers.
  Partial sales do not reduce the calculated age.
- Multi-company support is not included in this version.
- Data may be up to 24 hours old between scheduled refreshes.

## Roadmap

- [ ] Add age threshold alerts (configurable by manager)
- [ ] Add FIFO-aware age calculation using stock valuation layers
- [ ] Add multi-company support
- [ ] Add optional Definition B: days since last outgoing move

## Author

Onur Aksoy
[github.com/0nurAksoy](https://github.com/0nurAksoy)
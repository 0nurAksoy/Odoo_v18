# Restaurant Management (`oa_restaurant_ms`)

A small restaurant front-of-house addon for Odoo 18 Community: sections,
numbered tables, waiter assignment, table orders and a manager sales dashboard.

## Roles (security groups)

| Group | Can do |
|-------|--------|
| **Waiter / Waitress** | Take orders, add/remove products, apply **line** discounts — only on tables of the sections assigned to them. |
| **Head Waiter** | Everything a waiter can do, plus manage sections & tables and see **all** orders. |
| **Manager** | Full access, including the **global** (whole-bill) discount and the reporting dashboard. |

## Data model

- `oa.restaurant.section` — a floor/area; owns tables and a list of assigned waiters.
- `oa.restaurant.table` — a numbered table (unique number per section); status is *Free/Occupied* derived from its open orders.
- `oa.restaurant.order` — the bill (sequence `REST/00001`), with state `draft → confirmed → paid` (or `cancel`).
- `oa.restaurant.order.line` — a product on a bill, with quantity, unit price (from list price) and a line discount.
- `oa.restaurant.sales.report` — a read-only SQL view powering the graph/pivot dashboard (daily / monthly / yearly).

## Menus

`Restaurant` → *Orders* (take orders), *Tables* (floor kanban), *Reporting → Sales Report* (manager), *Configuration → Sections*.

## Demo data

Two helper scripts under `scripts/` populate the Sales Report with randomised
data. They run through the Odoo shell (the module must already be installed on
the target DB) and **commit** their changes. They are keyed off the
deterministic `oa_demo_*` user logins, so they never touch records you created
by hand. Replace `YOUR_DB` with your database name. (Don't use the
angle-bracket form `<db>` on the command line — the shell treats `<` and `>` as
redirection.)

Generate ~180 random orders spread over the last 12 months (re-run to top up):

```bash
/opt/odoo/venv/bin/python /opt/odoo/odoo/odoo-bin shell \
  -c /opt/odoo/odoo.conf -d YOUR_DB --no-http \
  < ~/Desktop/Odoo_v18/oa_restaurant_ms/scripts/generate_demo_orders.py
```

Clean up the demo data (deletes only the demo orders by default; set
`FULL_RESET = True` at the top of the script to also drop demo sections/tables
and archive demo users):

```bash
/opt/odoo/venv/bin/python /opt/odoo/odoo/odoo-bin shell \
  -c /opt/odoo/odoo.conf -d YOUR_DB --no-http \
  < ~/Desktop/Odoo_v18/oa_restaurant_ms/scripts/cleanup_demo_orders.py
```

Typical loop while tuning the dashboard: **cleanup → generate → refresh Sales Report**.

## Tests

`tests/test_restaurant_order.py` and `tests/test_restaurant_security.py` cover
staff/section/table creation, adding/changing/deleting products, line & global
discounts, the state flow, table-number uniqueness and the record-rule /
manager-discount access checks.

Run with (first install uses `-i`; use `-u` to re-run tests on an
already-installed module, since `--test-enable` only runs tests for modules
installed/upgraded in that run):

```bash
/opt/odoo/venv/bin/python /opt/odoo/odoo/odoo-bin \
  -c /opt/odoo/odoo.conf -d YOUR_DB -u oa_restaurant_ms --test-enable --stop-after-init
```

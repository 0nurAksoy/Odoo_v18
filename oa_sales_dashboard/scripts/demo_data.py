# Demo data for oa_sales_dashboard — real confirmed sale orders.
#
# The dashboard reads sale.report LIVE, so seeded orders appear on the next
# dashboard load; no cron/snapshot involved. Service products create no
# stock pickings, so cleanup is a clean cancel + unlink.
#
# EASIEST WAY TO RUN (one line, no pasting into a REPL, service can stay up —
# `odoo-bin shell` never binds port 8069):
#
#   seed:
#     /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/odoo.conf -d odoo18_dev < /home/onur/Desktop/Odoo_v18/oa_sales_dashboard/scripts/demo_data.py
#   clear:
#     OA_DEMO=clear /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /opt/odoo/odoo.conf -d odoo18_dev < /home/onur/Desktop/Odoo_v18/oa_sales_dashboard/scripts/demo_data.py
#
# Or interactively inside the shell:
#   exec(open('/home/onur/Desktop/Odoo_v18/oa_sales_dashboard/scripts/demo_data.py').read())
#   seed_demo()
#   clear_demo()

import os
import random
from datetime import date, datetime, time, timedelta

DEMO_TAG = "OA_DEMO"   # marker on client_order_ref + partner/product/warehouse names


def _say(msg):
    print(f"[{DEMO_TAG}] {msg}", flush=True)


def _demo_products(e):
    Product = e['product.template']
    products = Product.search([('name', 'like', DEMO_TAG)])
    if products:
        _say(f"reusing {len(products)} demo products")
        return products
    specs = [
        ("Consulting Hour", 120.0, 60.0),
        ("Support Pack", 300.0, 90.0),
        ("Onboarding Service", 800.0, 250.0),
        ("Training Day", 1500.0, 500.0),
        ("Custom Module", 2500.0, 900.0),
    ]
    products = Product.create([{
        'name': f"{DEMO_TAG} {name}",
        'type': 'service',          # no inventory -> no pickings -> clean cleanup
        'list_price': price,
        'standard_price': cost,     # cost drives margin via sale_margin
    } for (name, price, cost) in specs])
    _say(f"created {len(products)} demo products")
    return products


def _demo_partners(e):
    Partner = e['res.partner']
    partners = Partner.search([('name', 'like', DEMO_TAG)])
    if partners:
        _say(f"reusing {len(partners)} demo customers")
        return partners
    partners = Partner.create([
        {'name': f"{DEMO_TAG} Customer {i}", 'customer_rank': 1}
        for i in range(1, 6)
    ])
    _say(f"created {len(partners)} demo customers")
    return partners


def _demo_warehouses(e):
    """The 'Revenue by Branch' pie needs >= 2 warehouses to look like a pie."""
    Warehouse = e['stock.warehouse']
    warehouses = Warehouse.search([('company_id', '=', e.company.id)])
    if len(warehouses) < 2:
        warehouses += Warehouse.create({
            'name': f"{DEMO_TAG} Branch",
            'code': 'DEMO',         # short name, max 5 chars
        })
        _say("created second warehouse 'OA_DEMO Branch' for the branch pie")
    return warehouses


def seed_demo(days=180, n_orders=250, n_today=6):
    """Create demo orders: `n_today` dated today (for the Orders Today tile),
    the rest spread over the last `days` days (6 months feeds the line chart).
    """
    if 'env' not in globals():
        raise SystemExit("Run inside `odoo-bin shell` — see the header of this file.")
    e = env(context=dict(env.context, tracking_disable=True))   # skip mail tracking

    products = _demo_products(e).product_variant_ids
    partners = _demo_partners(e)
    warehouses = _demo_warehouses(e)
    today = date.today()

    order_vals = []
    for _ in range(n_orders):
        lines = [(0, 0, {
            'product_id': random.choice(products).id,
            'product_uom_qty': random.randint(1, 8),
        }) for _ in range(random.randint(1, 3))]
        order_vals.append({
            'partner_id': random.choice(partners).id,
            'warehouse_id': random.choice(warehouses).id,
            'client_order_ref': DEMO_TAG,
            'order_line': lines,
        })
    orders = e['sale.order'].create(order_vals)
    _say(f"created {len(orders)} draft orders")

    orders.action_confirm()   # -> state 'sale' (no email: send_email not in context)
    _say("confirmed all orders")

    # action_confirm() resets date_order to now() -> backdate AFTER confirming.
    # The first n_today orders keep today's date.
    for i, order in enumerate(orders):
        day = today if i < n_today else today - timedelta(days=random.randint(0, days - 1))
        order.date_order = datetime.combine(
            day, time(hour=random.randint(8, 16), minute=random.randint(0, 59)))
        if (i + 1) % 50 == 0:
            _say(f"backdated {i + 1}/{len(orders)}…")

    env.cr.commit()
    _say(f"DONE — {len(orders)} confirmed orders over {days} days across "
         f"{len(warehouses)} branches. Committed. Reload the dashboard.")


def clear_demo():
    """Remove everything seed_demo created (warehouse is archived, not deleted)."""
    if 'env' not in globals():
        raise SystemExit("Run inside `odoo-bin shell` — see the header of this file.")

    orders = env['sale.order'].search([('client_order_ref', '=', DEMO_TAG)])
    # sale.order can only be unlinked in draft/cancel -> cancel first
    orders.filtered(lambda o: o.state == 'sale')._action_cancel()
    orders.unlink()
    env.cr.commit()
    _say(f"removed {len(orders)} orders")

    warehouses = env['stock.warehouse'].search([('name', 'like', DEMO_TAG)])
    if warehouses:
        warehouses.action_archive()   # unlink is blocked once a warehouse was used
        env.cr.commit()
        _say(f"archived {len(warehouses)} demo warehouse(s)")

    # masters are best-effort, each in its own transaction
    for model in ('product.template', 'res.partner'):
        records = env[model].search([('name', 'like', DEMO_TAG)])
        if not records:
            continue
        try:
            records.unlink()
            env.cr.commit()
            _say(f"removed {len(records)} {model}")
        except Exception as exc:
            env.cr.rollback()
            _say(f"kept {len(records)} {model} (still referenced): {exc}")


# When piped via stdin, odoo shell executes this file with __name__ == '__main__'
# (interactive exec() leaves __name__ unset, so nothing auto-runs there).
if globals().get('__name__') == '__main__':
    _action = os.environ.get('OA_DEMO', 'seed').strip().lower()
    _say(f"auto-run: {_action}")
    clear_demo() if _action == 'clear' else seed_demo()

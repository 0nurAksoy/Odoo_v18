import os
import random
from datetime import date, datetime, time, timedelta

DEMO_TAG = "OA_DEMO"


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
        'type': 'service',
        'list_price': price,
        'standard_price': cost,
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

    if 'env' not in globals():
        raise SystemExit("Run inside `odoo-bin shell` — see the header of this file.")
    e = env(context=dict(env.context, tracking_disable=True))

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

    orders.action_confirm()
    _say("confirmed all orders")


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

    if 'env' not in globals():
        raise SystemExit("Run inside `odoo-bin shell` — see the header of this file.")

    orders = env['sale.order'].search([('client_order_ref', '=', DEMO_TAG)])

    orders.filtered(lambda o: o.state == 'sale')._action_cancel()
    orders.unlink()
    env.cr.commit()
    _say(f"removed {len(orders)} orders")

    warehouses = env['stock.warehouse'].search([('name', 'like', DEMO_TAG)])
    if warehouses:
        warehouses.action_archive()
        env.cr.commit()
        _say(f"archived {len(warehouses)} demo warehouse(s)")


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



if globals().get('__name__') == '__main__':
    _action = os.environ.get('OA_DEMO', 'seed').strip().lower()
    _say(f"auto-run: {_action}")
    clear_demo() if _action == 'clear' else seed_demo()

# -*- coding: utf-8 -*-
"""
Demo data generator for oa_restaurant_ms.

Creates sections, tables, a menu, waiters/manager and a batch of randomised
orders spread over the last ~12 months so the Sales Report (day/month/year,
per waiter / section / product) has something interesting to show.

Run it through the Odoo shell (it needs a live `env`):

    odoo shell -c /opt/odoo/odoo.conf -d <your_db> --no-http \
        < /opt/odoo/custom-addons/oa_restaurant_ms/scripts/generate_demo_orders.py

The module `oa_restaurant_ms` must already be installed on <your_db>.
Re-running tops up more orders; sections/menu/staff are get-or-create.
"""
import random
from datetime import datetime, timedelta

# `env` is provided by the Odoo shell. Guard so a mistaken `python file.py`
# fails with a clear message instead of a confusing NameError.
try:
    env
except NameError:  # pragma: no cover
    raise SystemExit("Run this inside `odoo shell` (it needs the Odoo `env`).")

NB_ORDERS = 180          # >= 150 as requested
DAYS_BACK = 365          # spread orders across the last year

random.seed()            # truly random each run; set a value here for repeatable data

Section = env['oa.restaurant.section']
Table = env['oa.restaurant.table']
Order = env['oa.restaurant.order']
Product = env['product.product']
Users = env['res.users']

internal_group = env.ref('base.group_user')
waiter_group = env.ref('oa_restaurant_ms.group_oa_restaurant_waiter')
manager_group = env.ref('oa_restaurant_ms.group_oa_restaurant_manager')


def get_or_create_user(login, name, groups):
    user = Users.search([('login', '=', login)], limit=1)
    if not user:
        user = Users.create({
            'name': name,
            'login': login,
            'email': '%s@example.com' % login,
            'groups_id': [(6, 0, [g.id for g in groups])],
        })
    return user


def get_or_create_section(name, code, waiters):
    section = Section.search([('name', '=', name)], limit=1)
    if not section:
        section = Section.create({
            'name': name,
            'code': code,
            'waiter_ids': [(6, 0, waiters.ids)],
        })
    return section


def get_or_create_table(section, number, waiter):
    table = Table.search([
        ('section_id', '=', section.id), ('table_number', '=', number),
    ], limit=1)
    if not table:
        table = Table.create({
            'section_id': section.id,
            'table_number': number,
            'seats': random.choice([2, 2, 4, 4, 6]),
            'waiter_id': waiter.id,
        })
    return table


def get_or_create_product(name, price):
    product = Product.search([('name', '=', name)], limit=1)
    if not product:
        product = Product.create({'name': name, 'list_price': price})
    return product


# --------------------------------------------------------------------------- #
#  Staff
# --------------------------------------------------------------------------- #
manager = get_or_create_user('oa_demo_manager', 'Demo Manager',
                             [internal_group, manager_group])
waiters = Users.browse()
for i in range(1, 6):
    waiters |= get_or_create_user('oa_demo_waiter_%d' % i, 'Demo Waiter %d' % i,
                                  [internal_group, waiter_group])

# --------------------------------------------------------------------------- #
#  Sections + tables (split the waiters across sections)
# --------------------------------------------------------------------------- #
sections = [
    get_or_create_section('Main Hall', 'MH', waiters[0:2]),
    get_or_create_section('Terrace', 'TR', waiters[2:4]),
    get_or_create_section('VIP Lounge', 'VIP', waiters[4:5]),
]

tables = Table.browse()
for section in sections:
    section_waiters = section.waiter_ids or waiters
    for number in range(1, random.randint(6, 9)):
        tables |= get_or_create_table(
            section, number, random.choice(section_waiters))

# --------------------------------------------------------------------------- #
#  Menu
# --------------------------------------------------------------------------- #
MENU = [
    ('Cheeseburger', 120.0), ('Margherita Pizza', 150.0), ('Caesar Salad', 90.0),
    ('Grilled Salmon', 220.0), ('Spaghetti Bolognese', 130.0), ('Steak', 280.0),
    ('French Fries', 45.0), ('Tomato Soup', 60.0), ('Tiramisu', 70.0),
    ('Cheesecake', 75.0), ('Cola', 25.0), ('Fresh Orange Juice', 40.0),
    ('Espresso', 30.0), ('Cappuccino', 38.0), ('House Wine (glass)', 85.0),
]
products = [get_or_create_product(name, price) for name, price in MENU]

# A few real partners to attach to some bills as customers (optional field).
partners = env['res.partner'].search([('is_company', '=', False)], limit=30) \
    or env['res.partner'].search([], limit=30)

# --------------------------------------------------------------------------- #
#  Orders
# --------------------------------------------------------------------------- #
STATES = (['paid'] * 70) + (['confirmed'] * 15) + (['draft'] * 10) + (['cancel'] * 5)
DISCOUNTS = [0, 0, 0, 0, 0, 5, 10, 15]   # mostly no line discount

created = 0
discounted_global = 0
for _ in range(NB_ORDERS):
    table = random.choice(tables)
    section = table.section_id
    waiter = table.waiter_id or random.choice(section.waiter_ids or waiters)

    # random datetime within business hours over the last DAYS_BACK days
    moment = datetime.now() - timedelta(
        days=random.randint(0, DAYS_BACK),
        hours=random.randint(0, 11),         # 11:00 .. 22:xx
        minutes=random.randint(0, 59),
    )
    moment = moment.replace(hour=random.randint(11, 22))

    line_cmds = []
    for product in random.sample(products, random.randint(1, 5)):
        line_cmds.append((0, 0, {
            'product_id': product.id,
            'quantity': random.randint(1, 4),
            'discount': random.choice(DISCOUNTS),
        }))

    order = Order.create({
        'table_id': table.id,
        'waiter_id': waiter.id,
        'partner_id': random.choice(partners).id if (partners and random.random() < 0.6) else False,
        'order_date': moment.strftime('%Y-%m-%d %H:%M:%S'),
        'state': random.choice(STATES),
        'line_ids': line_cmds,
    })

    # ~15% of orders get a manager-approved whole-bill discount.
    # Written *as the manager* so the manager-only guard is satisfied.
    if random.random() < 0.15:
        order.with_user(manager).write({'global_discount': random.choice([5, 10, 15, 20])})
        discounted_global += 1

    created += 1

env.cr.commit()

print("=" * 60)
print("oa_restaurant_ms demo data generated")
print("  staff      : 1 manager, %d waiters" % len(waiters))
print("  sections   : %d" % len(sections))
print("  tables     : %d" % len(tables))
print("  menu items : %d" % len(products))
print("  orders     : %d (this run) | %d with a global discount"
      % (created, discounted_global))
print("  total orders in db: %d" % Order.search_count([]))
print("=" * 60)
print("Open Restaurant > Reporting > Sales Report (as Manager) to explore.")

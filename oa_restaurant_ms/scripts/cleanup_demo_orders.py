# -*- coding: utf-8 -*-
"""
Cleanup for the oa_restaurant_ms demo data created by generate_demo_orders.py.

It identifies demo data through the deterministic `oa_demo_*` user logins, so
it will NOT touch sections / tables / orders you created by hand.

Run it through the Odoo shell (it needs a live `env`):

    odoo shell -c /opt/odoo/odoo.conf -d <your_db> --no-http \
        < ~/Desktop/Odoo_v18/oa_restaurant_ms/scripts/cleanup_demo_orders.py

Behaviour:
  * Default (safe)      -> deletes only the demo ORDERS (lines cascade).
                           Staff / sections / tables stay, so a re-run of the
                           generator just refills orders on the same layout.
  * FULL_RESET = True   -> also deletes the demo sections (their tables cascade)
                           and archives the demo users. Flip the flag below.
"""
try:
    env
except NameError:  # pragma: no cover
    raise SystemExit("Run this inside `odoo shell` (it needs the Odoo `env`).")

FULL_RESET = False   # set to True for a deeper teardown (sections + users)

Users = env['res.users']
Order = env['oa.restaurant.order']
Section = env['oa.restaurant.section']

# --- demo data is everything tied to the oa_demo_* accounts ----------------- #
demo_users = Users.with_context(active_test=False).search([('login', '=like', 'oa_demo_%')])
demo_sections = Section.search([('waiter_ids', 'in', demo_users.ids)]) if demo_users else Section.browse()

# Orders taken by a demo waiter or sitting in a demo section.
domain = ['|', ('waiter_id', 'in', demo_users.ids), ('section_id', 'in', demo_sections.ids)]
demo_orders = Order.search(domain) if demo_users else Order.browse()

n_orders = len(demo_orders)
demo_orders.unlink()   # order lines cascade (ondelete='cascade')

n_sections = n_tables = n_users = 0
if FULL_RESET:
    n_tables = len(demo_sections.table_ids)
    n_sections = len(demo_sections)
    demo_sections.unlink()          # tables cascade (table.section_id ondelete='cascade')
    n_users = len(demo_users)
    demo_users.write({'active': False})   # archive (safer than deleting users)

env.cr.commit()

print("=" * 60)
print("oa_restaurant_ms demo cleanup (FULL_RESET=%s)" % FULL_RESET)
print("  orders deleted   : %d" % n_orders)
if FULL_RESET:
    print("  sections deleted : %d" % n_sections)
    print("  tables  deleted  : %d" % n_tables)
    print("  users archived   : %d" % n_users)
print("  orders left in db: %d" % Order.search_count([]))
print("=" * 60)

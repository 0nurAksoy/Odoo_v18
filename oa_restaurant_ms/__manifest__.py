{
    'name': 'Restaurant Management',
    'version': '18.0.1.0.0',
    'category': 'Services/Restaurant',
    'author': 'Onur Aksoy',
    'website': 'https://github.com/0nurAksoy/Odoo_v18',
    'summary': 'Manage restaurant sections, numbered tables, waiters and table '
               'orders with daily/monthly/yearly sales reporting',
    'description': '',
    'depends': ['base', 'product', 'mail'],
    'data': [
        'security/restaurant_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/restaurant_section_views.xml',
        'views/restaurant_table_views.xml',
        'views/restaurant_order_views.xml',
        'views/restaurant_sales_report_views.xml',
        'views/restaurant_menus.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}

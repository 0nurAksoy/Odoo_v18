{
    'name': 'TCMB Currency Sync',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'author': 'Onur Aksoy',
    'website': 'https://github.com/0nurAksoy/Odoo_v18/tree/main/tcmb_currency_sync',
    'summary': 'Automatically syncs USD and EUR exchange rates from the Turkish Central Bank (TCMB) into Odoo every day.',
    'description': 'Fetches official ForexBuying rates from TCMB XML feed and updates Odoo currency rates automatically via a scheduled job.',
    'depends': ['base', 'account'],
    'data': [
        'data/cron.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
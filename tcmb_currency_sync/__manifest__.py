{
    'name': 'TCMB Currency Sync',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'author': 'Onur Aksoy',
    'website': 'https://github.com/0nurAksoy/Odoo_v18',
    'summary': 'Synchronizes official daily TCMB USD/EUR exchange rates into Odoo.',
    'description': 'Fetches official TCMB ForexBuying rates from the daily XML feed and updates Odoo currency rates using a scheduled action.',
    'depends': ['base', 'account'],
    'data': [
        'data/cron.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
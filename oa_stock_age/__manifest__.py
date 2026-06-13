{
    'name' : 'Stock Age Report',
    'version' : '18.0.1.0.0',
    'category' : 'Inventory',
    'author' : 'Onur Aksoy',
    'website' : 'https://github.com/0nurAksoy/Odoo_v18',
    'summary' : 'Identify slow-moving stock by showing how long products have been in inventory',
    'description' : '',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_age_report_views.xml',
        'data/stock_age_cron.xml',
    ],
    'application' : False,
    'installable': True,
    'license' : 'LGPL-3',

}
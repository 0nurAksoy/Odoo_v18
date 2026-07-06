{
    'name' : 'Sales Dashboard',
    'version' : '18.0.1.0.0',
    'category' : 'Sales',
    'author' : 'Onur Aksoy',
    'website' : 'https://github.com/0nurAksoy/Odoo_v18',
    'summary' : 'Manager sales dashboard revenue, profit, turnover, by branch and campaing.',
    'description' : '',
    'depends': ['sale_management','sale_margin','sale_stock','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_kpi_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oa_sales_dashboard/static/src/**/*',
        ],
    },
    'application' : True,
    'installable': True,
    'license' : 'LGPL-3',
}
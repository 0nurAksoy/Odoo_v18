from odoo import fields, models, tools


class RestaurantSalesReport(models.Model):
    """Read-only SQL view used for the manager dashboard (graph + pivot).

    One row per order line. Reporting straight from a database view keeps the
    data live (no duplication / no cron) and is the standard Odoo pattern for
    analytic reports such as ``sale.report`` and ``pos.order.report``.
    """
    _name = 'oa.restaurant.sales.report'
    _description = 'Restaurant Sales Report'
    _auto = False
    _rec_name = 'order_date'
    _order = 'order_date desc'

    order_id = fields.Many2one('oa.restaurant.order', string='Order', readonly=True)
    order_date = fields.Datetime(string='Order Date', readonly=True)
    waiter_id = fields.Many2one('res.users', string='Waiter', readonly=True)
    section_id = fields.Many2one('oa.restaurant.section', string='Section', readonly=True)
    table_id = fields.Many2one('oa.restaurant.table', string='Table', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ],
        string='Status', readonly=True,
    )
    quantity = fields.Float(string='Quantity', readonly=True)
    price_total = fields.Monetary(string='Total', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    l.id                AS id,
                    l.order_id          AS order_id,
                    o.order_date        AS order_date,
                    o.waiter_id         AS waiter_id,
                    o.section_id        AS section_id,
                    o.table_id          AS table_id,
                    l.product_id        AS product_id,
                    o.partner_id        AS partner_id,
                    o.company_id        AS company_id,
                    c.currency_id       AS currency_id,
                    o.state             AS state,
                    l.quantity          AS quantity,
                    l.price_subtotal * (1 - COALESCE(o.global_discount, 0) / 100.0) AS price_total
                FROM oa_restaurant_order_line l
                JOIN oa_restaurant_order o ON o.id = l.order_id
                JOIN res_company c ON c.id = o.company_id
            )
        """ % self._table)

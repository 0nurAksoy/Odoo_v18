from odoo import models, fields, api
from datetime import date, datetime


class StockAgeReport(models.Model):
    _name = 'stock.age.report'
    _description = 'Stock Age Report'
    _rec_name = 'product_id'
    _order = 'age_days desc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        readonly=True,
    )
    qty_on_hand = fields.Float(
        string='Quantity on Hand',
        readonly=True,
    )
    oldest_move_date = fields.Date(
        string='Oldest Incoming Date',
        readonly=True,
    )
    age_days = fields.Integer(
        string='Age (Days)',
        readonly=True,
    )
    last_refresh = fields.Datetime(
        string='Last Refreshed',
        readonly=True,
    )

    @api.model
    def action_refresh(self):
        self.sudo().search([]).unlink()

        quant_groups = self.env['stock.quant'].read_group(
            domain=[
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0),
            ],
            fields=['product_id', 'location_id', 'quantity:sum', 'in_date:min'],
            groupby=['product_id', 'location_id'],
            lazy=False,
        )

        if not quant_groups:
            return

        now = fields.Datetime.now()
        today = date.today()
        rows = []

        for group in quant_groups:
            oldest_date_raw = group['in_date']
            if not oldest_date_raw:
                continue

            if hasattr(oldest_date_raw, 'date'):
                oldest_date = oldest_date_raw.date()
            else:
                oldest_date = datetime.fromisoformat(
                    str(oldest_date_raw)
                ).date()

            age = (today - oldest_date).days

            rows.append({
                'product_id': group['product_id'][0],
                'location_id': group['location_id'][0],
                'qty_on_hand': group['quantity'],  # summed quantity
                'oldest_move_date': oldest_date,
                'age_days': age,
                'last_refresh': now,
            })

        if rows:
            self.sudo().create(rows)
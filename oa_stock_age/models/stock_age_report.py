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
            fields=['product_id', 'location_id', 'quantity:sum'],
            groupby=['product_id', 'location_id'],
            lazy=False,
        )

        if not quant_groups:
            return

        product_ids = [g['product_id'][0] for g in quant_groups]
        location_ids = [g['location_id'][0] for g in quant_groups]

        move_groups = self.env['stock.move'].read_group(
            domain=[
                ('product_id', 'in', product_ids),
                ('location_dest_id', 'in', location_ids),
                ('state', '=', 'done'),
            ],
            fields=['product_id', 'location_dest_id', 'date:min'],
            groupby=['product_id', 'location_dest_id'],
            lazy=False,
        )

        move_map = {}
        for group in move_groups:
            key = (group['product_id'][0], group['location_dest_id'][0])
            move_map[key] = group['date']

        now = fields.Datetime.now()
        today = date.today()
        rows = []

        for group in quant_groups:
            product_id = group['product_id'][0]
            location_id = group['location_id'][0]
            key = (product_id, location_id)

            oldest_date_raw = move_map.get(key)
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
                'product_id': product_id,
                'location_id': location_id,
                'qty_on_hand': group['quantity'],  # summed quantity
                'oldest_move_date': oldest_date,
                'age_days': age,
                'last_refresh': now,
            })

        if rows:
            self.sudo().create(rows)
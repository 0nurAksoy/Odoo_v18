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
        # Delete all existing rows
        self.sudo().search([]).unlink()

        # Get all products currently in stock at internal locations
        quants = self.env['stock.quant'].search([
            ('location_id.usage', '=', 'internal'),
            ('quantity', '>', 0),
        ])

        if not quants:
            return

        # Get oldest incoming move per product+location in ONE query
        move_groups = self.env['stock.move'].read_group(
            domain=[
                ('product_id', 'in', quants.mapped('product_id').ids),
                ('location_dest_id', 'in', quants.mapped('location_id').ids),
                ('state', '=', 'done'),
            ],
            fields=['product_id', 'location_dest_id', 'date:min'],
            groupby=['product_id', 'location_dest_id'],
            lazy=False,
        )

        # Build lookup dict: (product_id, location_id) → oldest date
        move_map = {}
        for group in move_groups:
            product_id = group['product_id'][0]
            location_id = group['location_dest_id'][0]
            move_map[(product_id, location_id)] = group['date']

        # Build rows
        now = fields.Datetime.now()
        today = date.today()
        rows = []

        for quant in quants:
            key = (quant.product_id.id, quant.location_id.id)
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
                'product_id': quant.product_id.id,
                'location_id': quant.location_id.id,
                'qty_on_hand': quant.quantity,
                'oldest_move_date': oldest_date,
                'age_days': age,
                'last_refresh': now,
            })

        if rows:
            self.sudo().create(rows)
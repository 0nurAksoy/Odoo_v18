from odoo import api, fields, models


class RestaurantOrderLine(models.Model):
    _name = 'oa.restaurant.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one(
        'oa.restaurant.order', string='Order',
        required=True, ondelete='cascade',
    )
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description', compute='_compute_name', store=True, readonly=False)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', compute='_compute_price_unit', store=True, readonly=False)
    discount = fields.Float(string='Discount (%)', default=0.0)
    currency_id = fields.Many2one(related='order_id.currency_id', string='Currency')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price

    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            net_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            line.price_subtotal = net_price * line.quantity

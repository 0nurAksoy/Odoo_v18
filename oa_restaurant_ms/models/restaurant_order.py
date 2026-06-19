from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RestaurantOrder(models.Model):
    _name = 'oa.restaurant.order'
    _description = 'Restaurant Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'order_date desc, id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False,
        readonly=True, default='New',
    )
    table_id = fields.Many2one('oa.restaurant.table', string='Table', required=True, tracking=True)
    table_number = fields.Integer(related='table_id.table_number', string='Table No.', store=True)
    section_id = fields.Many2one(related='table_id.section_id', string='Section', store=True)
    waiter_id = fields.Many2one(
        'res.users', string='Waiter', required=True, tracking=True,
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one('res.partner', string='Customer')
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency')
    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now, copy=False)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ],
        string='Status', default='draft', required=True, tracking=True,
    )
    line_ids = fields.One2many('oa.restaurant.order.line', 'order_id', string='Order Lines', copy=True)

    # Manager-only global discount on top of the whole bill.
    global_discount = fields.Float(string='Global Discount (%)', default=0.0, tracking=True)
    amount_untaxed = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True)
    amount_discount = fields.Monetary(string='Discount', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string='Total', compute='_compute_amounts', store=True)

    @api.depends('line_ids.price_subtotal', 'global_discount')
    def _compute_amounts(self):
        for order in self:
            subtotal = sum(order.line_ids.mapped('price_subtotal'))
            discount = subtotal * (order.global_discount or 0.0) / 100.0
            order.amount_untaxed = subtotal
            order.amount_discount = discount
            order.amount_total = subtotal - discount

    @api.constrains('global_discount')
    def _check_global_discount(self):
        for order in self:
            if order.global_discount < 0 or order.global_discount > 100:
                raise ValidationError('Global discount must be between 0 and 100%.')

    def _check_manager_discount(self):
        """Only managers may set a (non-zero) global discount."""
        if not self.env.user.has_group('oa_restaurant_ms.group_oa_restaurant_manager'):
            raise UserError('Only a Manager can apply a global discount.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('global_discount'):
                self._check_manager_discount()
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('oa.restaurant.order') or 'New'
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('global_discount'):
            self._check_manager_discount()
        return super().write(vals)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError('Cannot confirm an order without any products.')
            order.state = 'confirmed'

    def action_pay(self):
        for order in self:
            if order.state != 'confirmed':
                raise UserError('Only confirmed orders can be marked as paid.')
            order.state = 'paid'

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

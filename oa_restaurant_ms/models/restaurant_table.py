from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantTable(models.Model):
    _name = 'oa.restaurant.table'
    _description = 'Restaurant Table'
    _order = 'section_id, table_number'

    table_number = fields.Integer(string='Table Number', required=True)
    name = fields.Char(string='Table', compute='_compute_name', store=True)
    section_id = fields.Many2one(
        'oa.restaurant.section', string='Section',
        required=True, ondelete='cascade',
    )
    company_id = fields.Many2one(related='section_id.company_id', string='Company', store=True)
    seats = fields.Integer(string='Seats', default=4)
    waiter_id = fields.Many2one('res.users', string='Assigned Waiter')
    order_ids = fields.One2many('oa.restaurant.order', 'table_id', string='Orders')
    active_order_id = fields.Many2one(
        'oa.restaurant.order', string='Current Order',
        compute='_compute_active_order',
    )
    state = fields.Selection(
        selection=[('free', 'Free'), ('occupied', 'Occupied')],
        string='Status', default='free',
        compute='_compute_state', store=True,
    )

    _sql_constraints = [
        ('table_number_uniq_per_section',
         'unique(section_id, table_number)',
         'Table number must be unique within a section.'),
    ]

    @api.depends('section_id', 'section_id.code', 'section_id.name', 'table_number')
    def _compute_name(self):
        for table in self:
            prefix = table.section_id.code or table.section_id.name or ''
            table.name = '%s-%s' % (prefix, table.table_number) if prefix else str(table.table_number)

    @api.depends('order_ids.state')
    def _compute_active_order(self):
        for table in self:
            open_orders = table.order_ids.filtered(lambda o: o.state in ('draft', 'confirmed'))
            table.active_order_id = open_orders[:1]

    @api.depends('order_ids.state')
    def _compute_state(self):
        for table in self:
            open_orders = table.order_ids.filtered(lambda o: o.state in ('draft', 'confirmed'))
            table.state = 'occupied' if open_orders else 'free'

    @api.constrains('table_number')
    def _check_table_number(self):
        for table in self:
            if table.table_number <= 0:
                raise ValidationError('Table number must be a positive integer.')

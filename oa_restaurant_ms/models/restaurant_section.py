from odoo import api, fields, models


class RestaurantSection(models.Model):
    _name = 'oa.restaurant.section'
    _description = 'Restaurant Section'
    _order = 'name'

    name = fields.Char(string='Section Name', required=True)
    code = fields.Char(string='Code', help='Short code shown in table names, e.g. "MH" for Main Hall.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    # Waiters responsible for this section. Used by the order record rule so a
    # waiter only sees orders of the sections assigned to them.
    waiter_ids = fields.Many2many('res.users', string='Assigned Waiters')
    table_ids = fields.One2many('oa.restaurant.table', 'section_id', string='Tables')
    table_count = fields.Integer(string='Tables', compute='_compute_table_count')

    @api.depends('table_ids')
    def _compute_table_count(self):
        for section in self:
            section.table_count = len(section.table_ids)

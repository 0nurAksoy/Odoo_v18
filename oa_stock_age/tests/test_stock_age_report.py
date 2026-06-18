from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import date, timedelta


@tagged('at_install')
class TestStockAgeReport(TransactionCase):

    def setUp(self):
        super().setUp()

        self.supplier_loc = self.env.ref('stock.stock_location_suppliers')
        self.stock_loc = self.env.ref('stock.stock_location_stock')

        products = self.env['product.product'].search(
            [('is_storable', '=', True)],
            limit=2,
        )
        if len(products) < 2:
            self.skipTest("Need at least 2 storable products in the database")

        self.product = products[0]
        self.product_2 = products[1]

        self.move = self.env['stock.move'].create({
            'name': 'Test Incoming Move',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 8.0,
            'location_id': self.supplier_loc.id,
            'location_dest_id': self.stock_loc.id,
            'state': 'done',
            'date': date.today() - timedelta(days=120),
        })

        self.quant = self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.stock_loc.id,
            'quantity': 8.0,
            'in_date': self.move.date,
        })

    def test_refresh_creates_rows(self):
        self.env['stock.age.report'].action_refresh()
        records = self.env['stock.age.report'].search([
            ('product_id', '=', self.product.id)
        ])
        self.assertTrue(records)

    def test_age_days_calculated_correctly(self):
        self.env['stock.age.report'].action_refresh()

        record = self.env['stock.age.report'].search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', self.stock_loc.id),
        ], limit=1)

        expected_age = (date.today() - self.quant.in_date.date()).days
        self.assertEqual(record.age_days, expected_age)

    def test_refresh_replaces_data(self):
        self.env['stock.age.report'].action_refresh()
        self.env['stock.age.report'].action_refresh()
        records = self.env['stock.age.report'].search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', self.stock_loc.id),
        ])
        self.assertEqual(len(records), 1)

    def test_only_internal_locations(self):
        customer_loc = self.env.ref('stock.stock_location_customers')

        self.env['stock.move'].create({
            'name': 'Move to Customer',
            'product_id': self.product_2.id,
            'product_uom': self.product_2.uom_id.id,
            'product_uom_qty': 5.0,
            'location_id': self.stock_loc.id,
            'location_dest_id': customer_loc.id,
            'state': 'done',
            'date': date.today() - timedelta(days=50),
        })

        self.env['stock.quant'].create({
            'product_id': self.product_2.id,
            'location_id': customer_loc.id,
            'quantity': 5.0,
        })

        self.env['stock.age.report'].action_refresh()

        records = self.env['stock.age.report'].search([
            ('product_id', '=', self.product_2.id),
            ('location_id', '=', customer_loc.id),
        ])
        self.assertFalse(records)
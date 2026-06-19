from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestRestaurantOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        internal = cls.env.ref('base.group_user')
        waiter_group = cls.env.ref('oa_restaurant_ms.group_oa_restaurant_waiter')
        manager_group = cls.env.ref('oa_restaurant_ms.group_oa_restaurant_manager')

        cls.waiter = cls.env['res.users'].create({
            'name': 'Test Waiter',
            'login': 'oa_test_waiter',
            'email': 'oa_test_waiter@example.com',
            'groups_id': [(6, 0, [internal.id, waiter_group.id])],
        })
        cls.manager = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'oa_test_manager',
            'email': 'oa_test_manager@example.com',
            'groups_id': [(6, 0, [internal.id, manager_group.id])],
        })

        cls.section = cls.env['oa.restaurant.section'].create({
            'name': 'Main Hall',
            'code': 'MH',
            'waiter_ids': [(6, 0, [cls.waiter.id])],
        })
        cls.table = cls.env['oa.restaurant.table'].create({
            'table_number': 1,
            'section_id': cls.section.id,
            'seats': 4,
        })
        cls.burger = cls.env['product.product'].create({'name': 'Burger', 'list_price': 100.0})
        cls.cola = cls.env['product.product'].create({'name': 'Cola', 'list_price': 20.0})

    def _new_order(self):
        return self.env['oa.restaurant.order'].create({
            'table_id': self.table.id,
            'waiter_id': self.waiter.id,
        })

    def _add_line(self, order, product, qty=1.0, discount=0.0):
        return self.env['oa.restaurant.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'quantity': qty,
            'discount': discount,
        })

    # ------------------------------------------------------------------ #
    #  Setup data
    # ------------------------------------------------------------------ #
    def test_sequence_reference(self):
        order = self._new_order()
        self.assertNotEqual(order.name, 'New')
        self.assertTrue(order.name.startswith('REST/'))

    def test_table_number_unique_per_section(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.env['oa.restaurant.table'].create({
                    'table_number': 1,
                    'section_id': self.section.id,
                })
                self.env.flush_all()

    def test_table_number_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env['oa.restaurant.table'].create({
                'table_number': 0,
                'section_id': self.section.id,
            })

    # ------------------------------------------------------------------ #
    #  Products on the bill + totals
    # ------------------------------------------------------------------ #
    def test_add_products_and_totals(self):
        order = self._new_order()
        line = self._add_line(order, self.burger, qty=2)
        self._add_line(order, self.cola, qty=3)
        # unit price comes from the product list price
        self.assertEqual(line.price_unit, 100.0)
        # 2 * 100 + 3 * 20 = 260
        self.assertEqual(order.amount_untaxed, 260.0)
        self.assertEqual(order.amount_total, 260.0)

    def test_change_quantity_recomputes_total(self):
        order = self._new_order()
        line = self._add_line(order, self.burger, qty=1)
        self.assertEqual(order.amount_total, 100.0)
        line.quantity = 5
        self.assertEqual(order.amount_total, 500.0)

    def test_delete_line_recomputes_total(self):
        order = self._new_order()
        line = self._add_line(order, self.burger, qty=1)
        self.assertEqual(order.amount_total, 100.0)
        line.unlink()
        self.assertEqual(order.amount_total, 0.0)

    # ------------------------------------------------------------------ #
    #  Discounts
    # ------------------------------------------------------------------ #
    def test_line_discount(self):
        order = self._new_order()
        self._add_line(order, self.burger, qty=1, discount=10.0)
        # 100 * 0.9 = 90
        self.assertEqual(order.amount_total, 90.0)

    def test_global_discount_by_manager(self):
        order = self._new_order()
        self._add_line(order, self.burger, qty=1)
        order.with_user(self.manager).write({'global_discount': 50.0})
        self.assertEqual(order.amount_discount, 50.0)
        self.assertEqual(order.amount_total, 50.0)

    def test_global_discount_out_of_range(self):
        order = self._new_order()
        with self.assertRaises(ValidationError):
            order.with_user(self.manager).write({'global_discount': 150.0})

    # ------------------------------------------------------------------ #
    #  State flow + table status
    # ------------------------------------------------------------------ #
    def test_confirm_requires_lines(self):
        order = self._new_order()
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_state_flow(self):
        order = self._new_order()
        self._add_line(order, self.burger, qty=1)
        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')
        order.action_pay()
        self.assertEqual(order.state, 'paid')

    def test_table_status_follows_order(self):
        order = self._new_order()
        self._add_line(order, self.burger, qty=1)
        self.assertEqual(self.table.state, 'occupied')
        order.action_confirm()
        order.action_pay()
        self.assertEqual(self.table.state, 'free')

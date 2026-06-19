from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRestaurantSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        internal = cls.env.ref('base.group_user')
        waiter_group = cls.env.ref('oa_restaurant_ms.group_oa_restaurant_waiter')
        manager_group = cls.env.ref('oa_restaurant_ms.group_oa_restaurant_manager')

        cls.waiter_a = cls.env['res.users'].create({
            'name': 'Waiter A', 'login': 'oa_waiter_a', 'email': 'a@example.com',
            'groups_id': [(6, 0, [internal.id, waiter_group.id])],
        })
        cls.waiter_b = cls.env['res.users'].create({
            'name': 'Waiter B', 'login': 'oa_waiter_b', 'email': 'b@example.com',
            'groups_id': [(6, 0, [internal.id, waiter_group.id])],
        })
        cls.manager = cls.env['res.users'].create({
            'name': 'Manager', 'login': 'oa_manager', 'email': 'm@example.com',
            'groups_id': [(6, 0, [internal.id, manager_group.id])],
        })

        cls.section_a = cls.env['oa.restaurant.section'].create({
            'name': 'Section A', 'code': 'A',
            'waiter_ids': [(6, 0, [cls.waiter_a.id])],
        })
        cls.section_b = cls.env['oa.restaurant.section'].create({
            'name': 'Section B', 'code': 'B',
            'waiter_ids': [(6, 0, [cls.waiter_b.id])],
        })
        cls.table_a = cls.env['oa.restaurant.table'].create({
            'table_number': 1, 'section_id': cls.section_a.id,
        })
        cls.table_b = cls.env['oa.restaurant.table'].create({
            'table_number': 1, 'section_id': cls.section_b.id,
        })

    def _order_for(self, user, table):
        return self.env['oa.restaurant.order'].with_user(user).create({
            'table_id': table.id,
            'waiter_id': user.id,
        })

    def test_waiter_cannot_read_other_section_order(self):
        order_b = self._order_for(self.waiter_b, self.table_b)
        # Waiter A is not assigned to section B -> record rule blocks the read.
        with self.assertRaises(AccessError):
            order_b.with_user(self.waiter_a).read(['name'])

    def test_waiter_can_read_own_section_order(self):
        order_a = self._order_for(self.waiter_a, self.table_a)
        self.assertTrue(order_a.with_user(self.waiter_a).read(['name']))

    def test_manager_reads_all_orders(self):
        order_b = self._order_for(self.waiter_b, self.table_b)
        self.assertTrue(order_b.with_user(self.manager).read(['name']))

    def test_waiter_cannot_apply_global_discount(self):
        order_a = self._order_for(self.waiter_a, self.table_a)
        with self.assertRaises(UserError):
            order_a.with_user(self.waiter_a).write({'global_discount': 20.0})

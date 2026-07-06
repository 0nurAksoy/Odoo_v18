# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class SalesDashboardSnapshot(models.Model):
    _name = "oa.sales.dashboard.snapshot"
    _description = "Sales Dashboard Daily Snapshot"
    _order = "snapshot_date desc, id"
    _rec_name = "snapshot_date"

    snapshot_date = fields.Date(string="Date", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, index=True,
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id",
        store=True, readonly=True,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Branch", index=True,
    )
    revenue_untaxed = fields.Monetary(string="Revenue")   # price_subtotal
    revenue_total = fields.Monetary(string="Revenue (Total)")     # price_total
    margin = fields.Monetary(string="Margin")
    margin_percent = fields.Float(
        string="Margin (%)", compute="_compute_margin_percent",
    )
    product_uom_qty = fields.Float(string="Qty Ordered")
    line_count = fields.Integer(string="# of Lines")
    order_count = fields.Integer(string="# of Orders")

    @api.depends("margin", "revenue_untaxed")
    def _compute_margin_percent(self):
        for rec in self:
            rec.margin_percent = (
                rec.margin / rec.revenue_untaxed * 100.0
                if rec.revenue_untaxed else 0.0
            )

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------
    @api.model
    def _populate_for_date(self, day):
        """Rebuild snapshot rows for a single day from confirmed sales.

        :param day: datetime.date — the Order Date to aggregate.
        :return: number of rows written.
        """
        self = self.sudo()  # cron/backfill writes; bypass ACL safely
        start = fields.Datetime.to_datetime(day)
        end = fields.Datetime.to_datetime(day + timedelta(days=1))

        domain = [
            ("state", "=", "sale"),
            ("date", ">=", start),
            ("date", "<", end),
        ]
        groups = self.env["sale.report"].read_group(
            domain,
            fields=[
                "revenue_untaxed:sum(price_subtotal)",
                "revenue_total:sum(price_total)",
                "margin:sum(margin)",
                "product_uom_qty:sum(product_uom_qty)",
                "line_count:sum(nbr)",
                "order_count:count_distinct(order_reference)",
            ],
            groupby=["company_id", "warehouse_id"],
            lazy=False,
        )

        # idempotent: clear the day, then re-insert
        self.search([("snapshot_date", "=", day)]).unlink()

        vals_list = []
        for g in groups:
            if not g.get("company_id"):
                continue
            vals_list.append({
                "snapshot_date": day,
                "company_id": g["company_id"][0],
                "warehouse_id": g["warehouse_id"][0] if g["warehouse_id"] else False,
                "revenue_untaxed": g["revenue_untaxed"] or 0.0,
                "revenue_total": g["revenue_total"] or 0.0,
                "margin": g["margin"] or 0.0,
                "product_uom_qty": g["product_uom_qty"] or 0.0,
                "line_count": g["line_count"] or 0,
                "order_count": g["order_count"] or 0,
            })
        if vals_list:
            self.create(vals_list)
        return len(vals_list)

    @api.model
    def _populate_range(self, date_from, date_to):
        """Backfill snapshots for [date_from, date_to] inclusive."""
        day = date_from
        total = 0
        while day <= date_to:
            total += self._populate_for_date(day)
            day += timedelta(days=1)
        return total

    @api.model
    def _cron_build_daily_snapshot(self):
        """Daily cron: snapshot the last full day."""
        yesterday = fields.Date.context_today(self) - timedelta(days=1)
        self._populate_for_date(yesterday)

# -*- coding: utf-8 -*-
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import format_amount


class SalesKpi(models.Model):
    _name = "oa.sales.kpi"
    _description = "Sales Dashboard Data Provider"


    @api.model
    def get_dashboard_data(self):
        return {
            "tiles": self._dashboard_tiles(),
            "charts": self._dashboard_charts(),
        }

    @api.model
    def _dashboard_tiles(self):
        currency = self.env.company.currency_id
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)

        m_start = fields.Datetime.to_datetime(month_start)
        m_end = fields.Datetime.to_datetime(month_start + relativedelta(months=1))
        d_start = fields.Datetime.to_datetime(today)
        d_end = fields.Datetime.to_datetime(today + timedelta(days=1))

        rev_total = self._sum("price_total", m_start, m_end)
        rev_untaxed = self._sum("price_subtotal", m_start, m_end)
        margin = self._sum("margin", m_start, m_end)
        orders_today = self._orders(d_start, d_end)

        money = lambda v: format_amount(self.env, v, currency)
        return [
            {"key": "rev_total_m", "label": "Revenue (This Month)",
             "value": money(rev_total), "color": "#3C5A78", "icon": "fa-money"},
            {"key": "rev_untaxed_m", "label": "Revenue excl. Tax (This Month)",
             "value": money(rev_untaxed), "color": "#28a745", "icon": "fa-line-chart"},
            {"key": "margin_m", "label": "Margin (This Month)",
             "value": money(margin), "color": "#7E60BF", "icon": "fa-percent"},
            {"key": "orders_today", "label": "Orders (Today)",
             "value": str(orders_today), "color": "#C0504D", "icon": "fa-shopping-cart"},
        ]


    @api.model
    def _dashboard_charts(self):
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        m_start = fields.Datetime.to_datetime(month_start)
        m_end = fields.Datetime.to_datetime(month_start + relativedelta(months=1))
        return {
            "revenue_by_branch": self._revenue_by_branch(m_start, m_end),
            "revenue_by_product": self._revenue_by_product(m_start, m_end),
            "revenue_by_month": self._revenue_by_month(),
        }

    @api.model
    def _revenue_by_branch(self, start, end):
        groups = self.env["sale.report"].read_group(
            self._base_domain(start, end),
            ["price_total:sum"], ["warehouse_id"], lazy=False)
        labels, values = [], []
        for g in groups:
            labels.append(g["warehouse_id"][1] if g["warehouse_id"] else "No Branch")
            values.append(round(g["price_total"] or 0.0, 2))
        return {"labels": labels, "values": values}

    @api.model
    def _revenue_by_product(self, start, end, top=5):
        groups = self.env["sale.report"].read_group(
            self._base_domain(start, end),
            ["price_total:sum"], ["product_id"], lazy=False)
        groups.sort(key=lambda g: g["price_total"] or 0.0, reverse=True)
        labels = [g["product_id"][1] for g in groups[:top]]
        values = [round(g["price_total"] or 0.0, 2) for g in groups[:top]]
        rest = sum((g["price_total"] or 0.0) for g in groups[top:])
        if rest:
            labels.append("Others")
            values.append(round(rest, 2))
        return {"labels": labels, "values": values}

    @api.model
    def _revenue_by_month(self, months=6):
        this_month = fields.Date.context_today(self).replace(day=1)
        labels, values = [], []
        for i in range(months - 1, -1, -1):
            m_start = this_month - relativedelta(months=i)
            start = fields.Datetime.to_datetime(m_start)
            end = fields.Datetime.to_datetime(m_start + relativedelta(months=1))
            labels.append(m_start.strftime("%b %Y"))
            values.append(round(self._sum("price_total", start, end), 2))
        return {"labels": labels, "values": values}

    @api.model
    def _base_domain(self, start, end):
        return [
            ("state", "=", "sale"),
            ("company_id", "in", self.env.companies.ids),
            ("date", ">=", start),
            ("date", "<", end),
        ]

    @api.model
    def _sum(self, field, start, end):
        groups = self.env["sale.report"].read_group(
            self._base_domain(start, end), [f"{field}:sum"], [])
        return (groups and groups[0][field]) or 0.0

    @api.model
    def _orders(self, start, end):
        groups = self.env["sale.report"].read_group(
            self._base_domain(start, end), ["order_reference:count_distinct"], [])
        return (groups[0].get("order_reference") if groups else 0) or 0

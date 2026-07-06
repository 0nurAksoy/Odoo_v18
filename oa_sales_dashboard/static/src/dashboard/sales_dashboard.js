/** @odoo-module **/

import { Component, useState, useRef, useEffect, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const CHART_COLORS = ["#3C5A78", "#28a745", "#7E60BF", "#C0504D", "#E8A33D", "#5BC0BE"];


class ChartCard extends Component {
    static template = "oa_sales_dashboard.ChartCard";
    static props = {
        title: String,
        type: String,
        data: Object,
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;


        onWillStart(async () => await loadBundle("web.chartjs_lib"));

        useEffect(() => {
            this.renderChart();
            return () => this.chart?.destroy();
        });
    }

    renderChart() {
        this.chart?.destroy();
        this.chart = new Chart(this.canvasRef.el, this.getConfig());
    }

    getConfig() {
        const { labels, values } = this.props.data;
        if (this.props.type === "pie") {
            return {
                type: "pie",
                data: {
                    labels,
                    datasets: [{ data: values, backgroundColor: CHART_COLORS }],
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "bottom" } },
                },
            };
        }
        return {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: this.props.title,
                    data: values,
                    borderColor: "#3C5A78",
                    backgroundColor: "rgba(60, 90, 120, 0.15)",
                    fill: "start",
                    tension: 0.3,
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
            },
        };
    }
}

export class SalesDashboard extends Component {
    static template = "oa_sales_dashboard.SalesDashboard";
    static components = { ChartCard };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ tiles: [], charts: null, loading: true });

        onWillStart(async () => {
            const data = await this.orm.call("oa.sales.kpi", "get_dashboard_data", []);
            this.state.tiles = data.tiles;
            this.state.charts = data.charts;
            this.state.loading = false;
        });
    }
}

registry.category("actions").add("oa_sales_dashboard.dashboard", SalesDashboard);

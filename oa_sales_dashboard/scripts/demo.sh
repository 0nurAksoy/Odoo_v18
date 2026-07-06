#!/bin/bash
# Seed or clear oa_sales_dashboard demo data.
#   bash demo.sh            -> seed
#   bash demo.sh clear      -> clear
#   bash demo.sh seed mydb  -> other database (default: odoo18_dev)
HERE="$(cd "$(dirname "$0")" && pwd)"
DB="${2:-odoo18_dev}"
OA_DEMO="${1:-seed}" /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell \
    -c /opt/odoo/odoo.conf -d "$DB" < "$HERE/demo_data.py"

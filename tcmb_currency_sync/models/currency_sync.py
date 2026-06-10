import requests
import xml.etree.ElementTree as ET
from odoo import api, models
from odoo.exceptions import UserError

class TCMBCurrencySync(models.Model):
    _name    = 'tcmb.currency.sync'
    _description = 'TCMB Currency Sync'

    @api.model
    def sync_rates(self):
        # --- FETCH FROM TCMB ---
        try:
            response = requests.get(
                'https://www.tcmb.gov.tr/kurlar/today.xml',
                timeout=10
            )
            root = ET.fromstring(response.content)
        except Exception as e:
            raise UserError(f'TCMB API error: {e}')

        # --- PARSE USD AND EUR ---
        rates = {}
        for currency in root.findall('Currency'):
            code = currency.get('CurrencyCode')
            if code in ['USD', 'EUR']:
                buying = currency.find('ForexBuying').text
                rates[code] = float(buying)

        if not rates:
            raise UserError('No USD or EUR rates found in TCMB response!')

        # --- PUSH TO ODOO ---
        from datetime import date
        today = str(date.today())
        for code, rate in rates.items():
            currency_id = self.env['res.currency'].search(
                [('name', '=', code)], limit=1
            )
            if not currency_id:
                continue

            existing = self.env['res.currency.rate'].search([
                ('currency_id', '=', currency_id.id),
                ('name', '=', today)
            ])

            if existing:
                existing.write({'company_rate': 1.0 / rate})
            else:
                self.env['res.currency.rate'].create({
                    'name'        : today,
                    'currency_id' : currency_id.id,
                    'company_rate' : 1.0 / rate
                })
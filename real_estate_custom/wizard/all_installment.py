# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class wizard_model(models.TransientModel):
    _name = 'all.installment.report'
    _description = 'ALL Installment Report'

    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Partners", )
    unit_ids = fields.Many2many(comodel_name="product.template", string="Units",
                                domain=[('is_property', '=', True), ('state', '=', 'sold')])

    @api.onchange('partner_ids')
    def onchange_partner_id(self):
        if self.partner_ids:
            units = self.env['ownership.contract'].search(
                [('partner_id', 'in', self.partner_ids.ids), ('state', '=', 'confirmed')]).mapped(
                'building_unit')
            return {
                'domain': {
                    'unit_ids': [('id', 'in', units.ids)]
                }
            }

    def action_search_all_inst(self):
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.partner_ids:
            domain.append(('contract_partner_id', 'in', self.partner_ids.ids))
        if self.unit_ids:
            domain.append(('contract_building_unit', 'in', self.unit_ids.ids))
        data = {
            'domain': domain,
            'docs': self.id,
        }
        return self.env.ref('real_estate_custom.all_inst_report').report_action([], data=data)


# TODO Sent To Report Your Custom Data
class AllInst(models.AbstractModel):
    _name = 'report.real_estate_custom.all_inst_report_template'

    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('real_estate_custom.all_inst_report_template')
        custom_data = None
        total_amount = 0
        docs = None
        if data:
            domain = data.get('domain') or []
            docs = data.get('docs')
            custom_data = self.env['loan.line.rs.own'].search(domain)
            if custom_data:
                total_amount = sum(custom_data.mapped('amount'))
        vals = {
            'doc_ids': docs,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docs),
            'all_inst': custom_data,
            'total_amount': total_amount,
        }
        return vals

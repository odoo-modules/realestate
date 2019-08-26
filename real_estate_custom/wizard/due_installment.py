# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class wizard_model(models.TransientModel):
    _name = 'due.installment.report'
    _rec_name = 'partner_id'
    _description = 'Due Installment Report'

    date_from = fields.Date(string="Date From", required=False,)
    date_to = fields.Date(string="Date To", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    unit_id = fields.Many2one(comodel_name="product.template", string="Unit", required=False,
                              domain=[('is_property', '=', True), ('state', '=', 'sold')])

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            units = self.env['ownership.contract'].search([('partner_id', '=', self.partner_id.id)]).mapped(
                'building_unit')
            return {
                'domain': {
                    'unit_id': [('id', 'in', units.ids)]
                }
            }

    def action_search_due_inst(self):
        domain = [('paid', '=', False)]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.partner_id:
            domain.append(('contract_partner_id', '=', self.partner_id.id))
        if self.unit_id:
            domain.append(('contract_building_unit', '=', self.unit_id.id))

        return {
            'name': _('Due Installment Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'loan.line.rs.own',
            'target': 'current',
            'domain': domain,
            'context': {
                'create': False,
                'edit': False,
            },
        }

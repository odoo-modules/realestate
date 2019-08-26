# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class account_voucher(models.Model):
    _inherit = "account.voucher"

    real_estate_ref = fields.Char('Real Estate Ref.')
    to_text = fields.Char('to_text', compute='_to_text')
    text_msg = fields.Text('Message')
    contract_unit = fields.Many2one('product.template', string='Contract Unit', compute='get_unit')
    contract_building = fields.Many2one('building', string='Contract Building', compute='get_building')

    # test = num2words(amount, lang='ar')

    @api.one
    @api.depends('amount', 'to_text')
    def _to_text(self):
        for voucher in self:
            test = num2words(voucher.amount, lang='ar')
            voucher.to_text = str(test)

    @api.one
    def get_unit(self):
        for voucher in self:
            voucher_contract = voucher.env['ownership.contract'].search([('name', '=', self.reference)])
            voucher.contract_unit = voucher_contract.building_unit

    @api.one
    def get_building(self):
        for voucher in self:
            voucher_contract = voucher.env['ownership.contract'].search([('name', '=', self.reference)])
            voucher.contract_building = voucher_contract.building

    @api.multi
    def proforma_voucher(self):
        self.action_move_line_create()
        for voucher in self:
            if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2] == 'OC':  # ownership contract
                for line in voucher.line_ids:
                    installment_id = line.installment_line_id
                    if line.price_unit < installment_id.due_amount:
                        installment_id.write({
                            'due_amount': installment_id.due_amount - line.price_unit,
                        })
                    elif line.price_unit >= installment_id.due_amount:
                        installment_id.write({
                            'due_amount': 0.0,
                            'paid': True,
                        })

            if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2] == 'RC':  # rental contract
                for line in voucher.line_ids:
                    installment_id = line.installment_line_id
                    if line.price_unit < installment_id.due_amount:
                        installment_id.write({
                            'due_amount': installment_id.due_amount - line.price_unit,
                        })
                    elif line.price_unit >= installment_id.due_amount:
                        installment_id.write({
                            'due_amount': 0.0,
                            'paid': True,
                        })


class account_voucher_line(models.Model):
    _inherit = "account.voucher.line"

    installment_line_id = fields.Many2one(comodel_name="loan.line.rs.own", string="Installment ID", required=False, )

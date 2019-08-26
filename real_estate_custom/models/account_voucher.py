# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class account_voucher(models.Model):
    _inherit = "account.voucher"

    real_estate_ref = fields.Char('Real Estate Ref.')

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

# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class wizard_model(models.TransientModel):
    _inherit = "customer.payment.refund"

    contract = fields.Many2one('ownership.contract', 'Ownership Contract', required=True,
                               domain="[('state','in',['confirmed'])]")

    def create_voucher(self, rec, type):
        journal_pool = self.env['account.journal']
        if type == 'sale':
            journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        else:
            journal = journal_pool.search([('type', '=', 'purchase')], limit=1)
        if not journal:
            raise UserError(_('Please set purchase accounting journal!'))
        voucher_obj = self.env['account.voucher']
        voucher_id = voucher_obj.create({'partner_id': rec.contract.partner_id.id,
                                         'account_id': rec.account.id,
                                         'pay_now': 'pay_now',
                                         'reference': rec.contract.name,
                                         'name': rec.contract.name,
                                         'voucher_type': type,
                                         'journal_id': journal.id,
                                         })
        return voucher_id

    def create_voucher_line(self, rec, voucher_id):
        voucher_line_obj = self.env['account.voucher.line']
        lines = self.env['loan.line.rs.own'].search([('loan_id', '=', rec.contract.id)])
        lines_ids = []
        for l in lines: lines_ids.append(l.id)
        loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(lines_ids)
        for line in loan_line_rs_own_obj:
            if line.paid:
                name = line.name + str(' Installment Refund regarding ownership contract # ') + rec.contract.name
                voucher_line_obj.create({
                    'voucher_id': voucher_id.id,
                    'name': name,
                    'price_unit': line.amount,
                    'account_id': rec.partner.property_account_payable_id.id,
                })

    def refund(self):
        for rec in self:
            contract = self.contract
            any_paid = False
            for line in rec.contract.loan_line:
                if line.paid:
                    any_paid = True
                    break
            if not any_paid:
                raise UserError(_('You can just cancel contract, no payments to refund!'))

            journal_pool = self.env['account.journal']
            journal = journal_pool.search([('type', '=', 'purchase')], limit=1)

            # contract.write({'state': 'cancel'})  # comment
            if rec.payment_method == 'cash':
                if not journal:
                    raise UserError(_('Please set purchase accounting journal!'))
                voucher_id = self.create_voucher(rec, type='purchase')
                self.create_voucher_line(rec, voucher_id)
                vouchers = [voucher_id.id]
                if self.apply_me(rec): vouchers.append(self.apply_me(rec))
                return {
                    'name': _('Vouchers'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', vouchers)],
                    'res_model': 'account.voucher',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                }

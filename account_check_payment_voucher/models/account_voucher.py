# -*- coding: utf-8 -*-
##############################################################################
#
#    Check Payment in Voucher
#   
#    Copyright © 2016 Basement720 Technology, Inc.
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of VG Report and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################



from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

#----------------------------------------------------------
# Entries
#----------------------------------------------------------


class AccountVoucher(models.Model):
    _inherit = "account.voucher"
    
    hide_check_payment = fields.Boolean(compute='_compute_hide_check_payment',
        help="Technical field used to hide the check_payment if the selected journal has not been set or the selected journal has a type neither in in bank nor cash")
    
    check_payment_transaction_ids = fields.One2many('check.payment.transaction.voucher', 'account_voucher_id', string="Check Information",
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.multi
    def write(self, vals):
        
        for rec in self:
            if 'journal_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.journal_id = vals['journal_id']
            if 'partner_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.partner_id = vals['partner_id']
            if 'currency_id' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    check_payment.currency_id = vals['currency_id']
            if 'voucher_type' in vals:
                for check_payment in rec.check_payment_transaction_ids:
                    if vals['voucher_type'] == 'sale':
                        check_payment.payment_type = 'inbound'
                    elif vals['voucher_type'] == 'purchase':
                        check_payment.payment_type = 'outbound'
        res = super(AccountVoucher, self).write(vals)
        
        return res
        
    @api.multi
    def action_move_line_create(self):
        res = super(AccountVoucher, self).action_move_line_create()
        for rec in self:
            for check_payment in rec.check_payment_transaction_ids:
                if check_payment.state == 'draft':
                    if rec.voucher_type == 'sale':
                        check_payment.action_receive()
                    if rec.voucher_type == 'purchase':
                        check_payment.action_issue()
                    
        return res
    
    @api.onchange('pay_now')
    def onchange_pay_now(self):
        
        #super(AccountVoucher, self).onchange_partner_id()
        
        if self.pay_now == 'pay_now':
            if self.check_payment_transaction_ids:
                for rec in self.check_payment_transaction_ids:
                    if self.voucher_type == 'sale':
                        rec.payment_type = 'inbound'
                    elif self.voucher_type == 'purchase':
                        rec.payment_type = 'outbound'
                    rec.journal_id = self.journal_id
            self.hide_check_payment = False
        else:
            #if self.check_payment_transaction_ids:
            #    self.check_payment_transaction_ids = {}
            self.hide_check_payment = True
        return {}
        
        
    @api.onchange('journal_id')
    def _onchange_journal(self):
        #super(AccountVoucher, self)._onchange_journal()
        if self.journal_id:
            if self.check_payment_transaction_ids:
                for rec in self.check_payment_transaction_ids:
                    rec.journal_id = self.journal_id
        return {}     
        
        
           
    @api.multi
    @api.depends('pay_now')
    def _compute_hide_check_payment(self):
        for voucher in self:
            if voucher.pay_now == 'pay_now':
                # if voucher.check_payment_transaction_ids:
                    # for rec in voucher.check_payment_transaction_ids:
                        # if voucher.voucher_type == 'sale':
                            # rec.payment_type = 'inbound'
                        # elif voucher.voucher_type == 'purchase':
                            # rec.payment_type = 'outbound'
                        # rec.journal_id = self.journal_id
                voucher.hide_check_payment = False
            else:
                voucher.hide_check_payment = True

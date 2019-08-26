# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class customer_payment_refund(models.TransientModel):
    _name = 'customer.payment.refund'
    
    account= fields.Many2one('account.account','Account', )
    contract= fields.Many2one('ownership.contract','Ownership Contract',required=True)
    partner= fields.Many2one('res.partner','Partner',required=True,domain=[('customer', '=', True)])
    journal= fields.Many2one('account.journal','Journal', )
    payment_method= fields.Selection([('cash','Cash'),('cheque','Cheque')], 'Payment Method', required=True, default='cash')
    managerial_expenses= fields.Float('Managerial Expenses (Amt.)')
    managerial_expenses_percent= fields.Float('Managerial Expenses (%)')
    
    @api.onchange('managerial_expenses')
    def onchange_managerial_expenses(self):
        if self.managerial_expenses>0:
            self.managerial_expenses_percent = 0

    @api.onchange('managerial_expenses_percent')
    def onchange_managerial_expenses_percent(self):
        if self.managerial_expenses_percent>0:
            self.managerial_expenses= 0.0

    @api.onchange('partner')
    def onchange_partner(self):
        if self.partner:
            contracts=[]
            contract_ids = self.env['ownership.contract'].search([('partner_id', '=', self.partner.id),('state','=','confirmed')])
            for obj in contract_ids:
                contracts.append(obj.id)
            return {'domain': {'contract': [('id', 'in', contracts)]}}

    def create_voucher(self, rec, type):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'purchase')], limit=1)
        if not journal:
            raise UserError(_('Please set purchase accounting journal!'))
        voucher_obj = self.env['account.voucher']
        voucher_id = voucher_obj.create({'partner_id':rec.contract.partner_id.id,
                  'account_id':rec.contract.partner_id.property_account_receivable_id.id,
                  'pay_now':'pay_now','reference':rec.contract.name,
                  'name': rec.contract.name,
                  'voucher_type': type,'journal_id':journal.id,
                  })
        return voucher_id

    def create_voucher_line(self, rec,voucher_id):
        voucher_line_obj = self.env['account.voucher.line']
        lines = self.env['loan.line.rs.own'].search([('loan_id', '=', rec.contract.id)])
        lines_ids=[]
        for l in lines: lines_ids.append(l.id)
        loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(lines_ids)
        for line in loan_line_rs_own_obj:
            if line.paid:
                name=line.name + str(' Installment Refund regarding ownership contract # ')+rec.contract.name
                voucher_line_obj.create(
                 {'voucher_id':voucher_id.id,'name':name,
                  'price_unit':line.amount,'account_id':rec.account.id})

    def apply_me(self, rec):
        voucher_line_obj = self.env['account.voucher.line']
        total=0
        for line in rec.contract.loan_line:
            if line.paid:
                total+=line.amount
        me_expense = rec.managerial_expenses + (rec.managerial_expenses_percent*total/100.0)
        me_account = self.env['res.config.settings'].browse(
            self.env['res.config.settings'].search([])[-1].id).default_me_account.id if self.env[
            'res.config.settings'].search([]) else ""
        if not me_account:
            raise UserError(_('Please set default Managerial Expenses Account!'))
        if me_expense:
            voucher_id = self.create_voucher(rec,type='sale')
            voucher_line_obj.create(
                     {'voucher_id':voucher_id.id,'name':'Managerial Expenses',
                      'price_unit':me_expense,'account_id':me_account})
            return voucher_id.id

    def refund(self):
        for rec in self:
            contract = self.contract
            any_paid=False
            for line in rec.contract.loan_line:
                if line.paid:
                    any_paid=True
                    break
            if not any_paid:
                raise UserError(_('You can just cancel contract, no payments to refund!'))

            journal_pool = self.env['account.journal']
            journal = journal_pool.search([('type', '=', 'purchase')], limit=1)

            contract.write({'state': 'cancel'})
            if rec.payment_method=='cash':
                if not journal:
                    raise UserError(_('Please set purchase accounting journal!'))
                voucher_id = self.create_voucher(rec, type='purchase')
                self.create_voucher_line(rec,voucher_id)
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
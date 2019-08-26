# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta

class customer_rental_payment_check(models.TransientModel):
    _name = 'customer.rental.payment.check'
    
    contract= fields.Many2one('rental.contract','Rental Contract',required=True)
    partner= fields.Many2one('res.partner','Partner',required=True,domain=[('customer', '=', True)])
    account= fields.Many2one('account.account','Account', )
    journal= fields.Many2one('account.journal','Journal', )
    loan_line= fields.One2many('loan.line.rs.rent.wizard', 'loan_id')
    payment_method= fields.Selection([('cash','Cash'),('cheque','Cheque')], 'Payment Method', required=True, default='cash')
    discount_cash_total= fields.Float('Discount (Amt.) ')
    discount_percent_total= fields.Float('Discount %')
    select_all= fields.Boolean('Select all') 
       
    @api.onchange('select_all')    
    def onchange_select(self):
        if self.contract:
            loan_lines=[]
            for line in self.contract.loan_line:
                if not line.paid:
                    if self.select_all:
                        loan_lines.append((0,0,{'to_be_paid':True, 'date':line.date,'amount':line.amount,'installment_line_id': line.id, 'name':line.name}))
                    else:
                        loan_lines.append((0,0,{'to_be_paid':False, 'date':line.date,'amount':line.amount,'installment_line_id': line.id, 'name':line.name}))
            return {'value': {'loan_line':loan_lines}}

    @api.onchange('discount_cash_total')
    def onchange_discount_cash(self):
        if self.discount_cash_total>0:
            self.discount_percent_total= 0.0

    @api.onchange('discount_percent_total')
    def onchange_discount_percent(self):
        if self.discount_percent_total>0:
            self.discount_cash_total= 0.0

    @api.onchange('partner')
    def onchange_partner(self):
        if self.partner:
            contracts=[]
            contract_ids = self.env['rental.contract'].search([('partner_id', '=', self.partner.id)])
            for obj in contract_ids:
                contracts.append(obj.id)
            return {'domain': {'contract': [('id', 'in', contracts)]}}

    @api.onchange('contract')
    def onchange_contract(self):
        if self.contract:
            loan_lines=[]
            for line in self.contract.loan_line:
                if not line.paid:
                    loan_lines.append((0,0,{'date':line.date,'amount':line.amount,'installment_line_id': line.id, 'name':line.name}))
            self.loan_line= loan_lines
            self.partner=self.contract.partner_id.id

    def create_voucher(self, rec, type):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        journal_p = journal_pool.search([('type', '=', 'purchase')], limit=1)
        if not journal_p:
            raise UserError(_('Please set purchase accounting journal!'))
        if type=='sale':
            journal_id= journal
        else:
            journal_id= journal_p
        voucher_obj = self.env['account.voucher']
        voucher_id = voucher_obj.create({'partner_id':rec.contract.partner_id.id,
                  'real_estate_ref':rec.contract.name,
                  'payment_journal_id': rec.journal.id,
                  'account_id': rec.journal.default_debit_account_id.id,
                  'name': rec.contract.name,
                  'pay_now':'pay_now','reference':rec.contract.name,
                  'voucher_type': type,'journal_id':journal_id.id,
                  })
        return voucher_id

    def apply_discount(self, rec):
        voucher_line_obj = self.env['account.voucher.line']
        lines_discount=0
        total_amount=0
        for line in rec.loan_line:
            if line.to_be_paid:
                lines_discount += (line.amount*line.discount_percent)/100.0+line.discount_cash
                total_amount+=line.amount
        total_discount = total_amount*rec.discount_percent_total/100.0 + rec.discount_cash_total
        total_discount += lines_discount

        if total_discount > 0:
            default_discount_account = self.env['res.config.settings'].browse(
                self.env['res.config.settings'].search([])[-1].id).default_discount_account.id if self.env[
                'res.config.settings'].search([]) else ""
            if not default_discount_account:
                raise UserError(_('Please set discount account in module configuration!'))
            voucher_id = self.create_voucher(rec,type='purchase')
            voucher_line_obj.create(
                {'voucher_id':voucher_id.id,'name':'Allowed Discount',
                 'price_unit':total_discount,'account_id':default_discount_account})
            return voucher_id.id

    def pay(self):
        penalty_obj = self.env['late.payment.penalties']
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        line_ids=[]
        total_penalties = 0
        for rec in self:          
            payment_method=rec.payment_method
            if payment_method=='cash':
                for rec in self:
                    for line in rec.loan_line:
                        if line.to_be_paid:
                            total_penalties+=penalty_obj.get_penalties(line)
                            line_ids.append(line.installment_line_id)
                    if line_ids:
                        if not rec.contract.partner_id.property_account_receivable_id.id:
                            raise UserError(_('Please set receivable account for Partner'))
                        voucher_id = self.create_voucher(rec,type='sale')
                        loan_line_rs_own_obj = self.env['loan.line.rs.rent'].browse(line_ids)
                        for line in loan_line_rs_own_obj:
                            name= str(' Regarding Rental Contract # ')+rec.contract.name
                            voucher_line_obj.create(
                                                    {'installment_line_id':line.id,'voucher_id':voucher_id.id,'name':name,
                                                    'price_unit':line.amount,'account_id':rec.contract.partner_id.property_account_receivable_id.id})
                        vouchers=[]
                        discount_voucher =self.apply_discount(rec)
                        if discount_voucher: vouchers.append(discount_voucher)
                        vouchers.append(voucher_id.id)
                        if total_penalties>0:
                            penalty_str=str(' Penalty on Rental Contract ')+str(rec.contract.name)
                            voucher_line_obj.create(
                            {'voucher_id':voucher_id.id,'name':penalty_str,
                             'price_unit':total_penalties,'account_id':penalty_obj.get_account(cr, uid)})

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
        # can be activated in case of receiving cheques
        if payment_method=='cheque':
            lines_discount=0
            total_amount=0
            for rec in self:     
                total_to_be_paid=0
                for line in rec.loan_line:
                    if line.to_be_paid:
                        lines_discount += (line.amount*line.discount_percent)+line.discount_cash
                        total_amount+=line.amount
                        total_penalties+=penalty_obj.get_penalties(line)
                        line_ids.append(line.installment_line_id)
                        total_to_be_paid+=total_penalties
                if line_ids:
                    if not rec.contract.partner_id.property_account_receivable_id.id:
                        raise UserError(_('Please set receivable account for Partner'))

                    loan_line_rs_own_obj = self.env['loan.line.rs.rent'].browse(line_ids)  
                    for line in loan_line_rs_own_obj:
                        line.write({'paid': True})
                        total_to_be_paid+=line.amount
                total_discount = total_amount*rec.discount_percent_total + rec.discount_cash_total
                total_discount += lines_discount
                total_to_be_paid += total_discount

                abs_pool = self.env['account.bank.statement']
                abs_line_pool = self.env['account.bank.statement.line']
                abs_id = abs_pool.create({
                          'real_estate_ref':rec.contract.name,
                          'partner_id':rec.contract.partner_id.id,
                          'journal_id':rec.journal.id,
                          'collect_ok':True,
                          'ref':rec.cheque_number,
                          })
                abs_line_pool.create({'partner_id':rec.contract.partner_id.id,
                          'statement_id':abs_id,
                          'amount':total_to_be_paid,
                          'ref':rec.cheque_number,
                          'name': 'Regarding Rental Contract # ' + str(rec.contract.name)
                          })
                mod_obj = self.env['ir.model.data']
                res = mod_obj.get_object_reference('bank_statement_mod', 'view_bank_statement_form_collect')
                res_id = res and res[1] or False
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': [res_id],
                    'res_model': 'account.bank.statement',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': abs_id,
                }

class loan_line_rs_rent_wizard(models.TransientModel):
    _name = 'loan.line.rs.rent.wizard'
    
    date= fields.Date('Date')
    name= fields.Char('Name')
    serial= fields.Char('#')
    empty_col= fields.Char(' ')
    amount= fields.Float('Payment', digits=(16, 4),)
    installment_line_id= fields.Integer('id ')
    to_be_paid= fields.Boolean('Pay')        
    loan_id= fields.Many2one('customer.rental.payment.check', '',ondelete='cascade', readonly=True)
    discount_cash= fields.Float('Discount (Amt.) ')
    discount_percent= fields.Float('Discount %')

    def onchange_discount_cash(self, discount):
        if discount>0:
            return {'value': {'discount_percent':0.0}}

    def onchange_discount_percent(self, discount):
        if discount>0:
            return {'value': {'discount_cash':0.0}}
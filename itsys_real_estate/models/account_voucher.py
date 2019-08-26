# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta
import sys

class account_voucher(models.Model):
    _inherit = "account.voucher"

    real_estate_ref= fields.Char('Real Estate Ref.')
    
    def proforma_voucher(self):
        res = super(account_voucher, self).proforma_voucher()
        for voucher in self:
            if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2]=='OC': #ownership contract
                for line in voucher.line_ids:
                    installment_line_id = line.installment_line_id
                    loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(installment_line_id)  
                    for line in loan_line_rs_own_obj:
                        line.write({'paid': True})   
            if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2]=='RC': #rental contract 
                for line in voucher.line_ids:
                    installment_line_id = line.installment_line_id
                    loan_line_rs_rent_obj = self.env['loan.line.rs.rent'].browse(installment_line_id)
                    for line in loan_line_rs_rent_obj:
                        line.write({'paid': True})
            """
            if (voucher.real_estate_ref)[:2]=='CC= #construction contract
                contract_pool = self.env['construction.contract']
                contract_id = contract_pool.search([('name', '=', voucher.real_estate_ref)], limit=1, ntext=context)
                contract_obj = contract_pool.browse(contract_id)  
                new_paid_amount = contract_obj.paid_amount + voucher.amount
                contract_obj.write({'paid_amount= new_paid_amount}) 
            if (voucher.real_estate_ref)[:3]=='SCC= #sub construction contract
                contract_pool = self.env['sub.construction.contract']
                contract_id = contract_pool.search([('name', '=', voucher.real_estate_ref)], limit=1, ntext=context)
                contract_obj = contract_pool.browse(contract_id)  
                new_paid_amount = contract_obj.paid_amount + voucher.amount
                contract_obj.write({'paid_amount= new_paid_amount})    
            """
        return res

class account_voucher_line(models.Model):
    _inherit = "account.voucher.line"
    installment_line_id= fields.Integer('installment_line_id.', )
    
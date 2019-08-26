# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Parser(models.AbstractModel):
    _name = 'report.itsys_real_estate.report_sales_rep'

    def _get_lines(self,start_date, end_date, salesperson_ids):
        result=[]
        if len(salesperson_ids)==0:
            contract_ids = self.env['ownership.contract'].search([('date','>=',start_date),('date','<=',end_date)])
            contracts=[]
            for obj in contract_ids: contracts.append(obj.id)
            contracts=self.env['ownership.contract'].browse(contracts)
            users=[]
            for c in contracts:
                users.append(c.user_id)
            salesperson_ids=users
            salesperson_ids = list(set(salesperson_ids))
        for person in salesperson_ids:
            lines=[]
            paid=0
            amount=0
            balance=0
            res={}
            contract_ids = self.env['ownership.contract'].search([('user_id', '=', person.id),('date','>=',start_date),('date','<=',end_date)])
            contracts=[]
            for obj in contract_ids: contracts.append(obj.id)
            contracts=self.env['ownership.contract'].browse(contracts)
            for contract in contracts:
                line = []
                line.append(contract.user_id.name)
                line.append(contract.name)
                line.append(contract.date)
                line.append(contract.city)
                line.append(contract.region)
                line.append(contract.building.name)
                line.append(contract.building_unit.name)

                paid_contract=0
                balance_contract=0
                total_contract=0
                for l in contract.loan_line:
                    if l.paid:
                        paid_contract+= l.amount
                for l in contract.loan_line:
                    if not l.paid:
                        balance_contract+= l.amount
                for l in contract.loan_line:
                    total_contract+= l.amount

                line.append(total_contract)
                line.append(paid_contract)
                line.append(balance_contract)

                lines.append(line)
                paid+=paid_contract
                amount+=total_contract
                balance+=balance_contract
            res['lines']=lines
            res['totals']=[amount,paid,balance]
            result.append(res)

        return result


    def _get_total(self,start_date, end_date, salesperson_ids):
        result=[]
        paid=0
        amount=0
        balance=0
        if len(salesperson_ids)==0:
            contract_ids = self.env['ownership.contract'].search([('date','>=',start_date),('date','<=',end_date)])
            contracts=[]
            for obj in contract_ids: contracts.append(obj.id)
            contracts=self.env['ownership.contract'].browse(contracts)
            users=[]
            for c in contracts:
                users.append(c.user_id)
            salesperson_ids=users
            salesperson_ids = list(set(salesperson_ids))
        for person in salesperson_ids:
            contract_ids = self.env['ownership.contract'].search([('user_id', '=', person.id),('date','>=',start_date),('date','<=',end_date)])
            contracts=[]
            for obj in contract_ids: contracts.append(obj.id)
            contracts=self.env['ownership.contract'].browse(contracts)
            for contract in contracts:
                paid+=contract.paid
                amount+=contract.total_amount
                balance+=contract.balance
            result=[[amount,paid,balance]]
        return result


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        sales_rep = self.env['ir.actions.report']._get_report_from_name('itsys_real_estate.report_sales_rep')

        return {
            'doc_ids': self.ids,
            'doc_model': sales_rep.model,
            'date_to': data['form']['date_to'],
            'date_from': data['form']['date_from'],
            'get_lines': self._get_lines(data['form']['date_from'], data['form']['date_to'], data['form']['user_ids']),
            'get_total': self._get_total(data['form']['date_from'], data['form']['date_to'], data['form']['user_ids']),
        }
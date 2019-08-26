# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date,timedelta

class Parser(models.AbstractModel):
    _name = 'report.itsys_real_estate.report_due_payments_units'

    def _get_lines(self,start_date, end_date, unit_ids):
        lines=[]
        if len(unit_ids)>0:
            contract_ids = self.env['ownership.contract'].search([('building_unit', 'in', unit_ids)])        
        else:
            contract_ids = self.env['ownership.contract'].search([])
        contracts=[]
        for obj in contract_ids: contracts.append(obj.id)

        contracts=self.env['ownership.contract'].browse(contracts)
        for contract in contracts:
            for line in contract.loan_line:
                if not line.paid and line.date>=start_date and line.date <=end_date:
                    lines.append(line)
        return lines

    def _get_total(self,start_date, end_date, unit_ids):
        sum=0
        if len(unit_ids)>0:
            contract_ids = self.env['ownership.contract'].search([('building_unit', 'in', unit_ids)])        
        else:
            contract_ids = self.env['ownership.contract'].search([])
        contracts=[]
        for obj in contract_ids: contracts.append(obj.id)
        contracts=self.env['ownership.contract'].browse(contracts)
        for contract in contracts:
            for line in contract.loan_line:
                if not line.paid and line.date>=start_date and line.date <=end_date:
                    sum+=line.amount
        return sum

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        due_payment = self.env['ir.actions.report']._get_report_from_name('itsys_real_estate.report_due_payments_units')
        return {
            'doc_ids': self.ids,
            'doc_model': due_payment.model,
            'date_start': data['form']['date_start'],
            'date_end': data['form']['date_end'],
            'get_lines': self._get_lines(data['form']['date_start'],data['form']['date_end'],data['form']['building_unit']),
            'get_total': self._get_total(data['form']['date_start'],data['form']['date_end'],data['form']['building_unit']),
        }
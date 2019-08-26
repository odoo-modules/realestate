# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
import calendar


class InstallmentRescheduling(models.TransientModel):
    _name = 'installment.rescheduling'

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, domain=[('customer', '=', True)])
    contract_id = fields.Many2one('ownership.contract', 'Ownership Contract', required=True)
    total_amount = fields.Float(string="Total Unpaid Amount", required=False, compute='compute_total_amount')
    reschedule_all = fields.Boolean('Reschedule All')
    template_id = fields.Many2one('installment.template', 'Payment Template')
    start_date = fields.Date(string="Start Date", )
    installment_ids = fields.One2many('installment.wizard', 'rescheduling_id')

    @api.depends('contract_id')
    def compute_total_amount(self):
        if self.contract_id:
            total_amount = 0
            for line in self.contract_id.loan_line:
                if not line.paid:
                    total_amount += line.amount
            self.total_amount = total_amount
        else:
            self.total_amount = 0

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.contract_id = False
            self.installment_ids = False
            return {
                'domain': {
                    'contract_id': [('partner_id', '=', self.partner_id.id)]
                }
            }
        else:
            self.contract_id = False
            self.installment_ids = False
            return {
                'domain': {
                    'contract_id': [('id', '=', False)]
                }
            }

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        if self.contract_id:
            unpaid_inst = []
            for line in self.contract_id.loan_line:
                if not line.paid:
                    unpaid_inst.append(
                        (0, 0, {'inst_id': line.id, 'name': line.name, 'date': line.date, 'amount': line.amount}))
            self.installment_ids = unpaid_inst
            self.env.cr.commit()

        else:
            self.installment_ids = False

    def action_reschedule(self):
        if self.reschedule_all:
            if self.template_id:
                unpaid_amount = self.total_amount
                self.delete_previouse_insts()
                self.create_insts(self.start_date, unpaid_amount)
        else:
            if self.installment_ids:
                self.check_insts_amount()
                self.delete_insts()

                for line in self.installment_ids:
                    inst_id = line.inst_id
                    if inst_id:
                        inst_id.sudo().write({
                            'name': line.name,
                            'date': line.date,
                            'amount': line.amount,
                        })
                    else:
                        self.env['loan.line.rs.own'].sudo().create({
                            'name': line.name,
                            'date': line.date,
                            'amount': line.amount,
                            'loan_id': self.contract_id.id,
                        })
                return True

    def delete_previouse_insts(self):
        for line in self.contract_id.loan_line:
            if not line.paid:
                line.sudo().unlink()

    def create_insts(self, first_date, amount):
        loan_obj = self.env['loan.line.rs.own'].sudo()
        pricing = amount
        mon = self.template_id.duration_month
        yr = self.template_id.duration_year
        repetition = self.template_id.repetition_rate
        advance_percent = self.template_id.adv_payment_rate
        deduct = self.template_id.deduct
        first_date = datetime.strptime(first_date, '%Y-%m-%d').date()
        adv_payment = pricing * float(advance_percent) / 100
        if mon > 12:
            x = mon / 12
            mon = (x * 12) + mon % 12
        mons = mon + (yr * 12)
        if adv_payment:
            loan_obj.create({'serial': 1, 'amount': adv_payment, 'date': first_date, 'name': _('Advance Payment'),
                             'loan_id': self.contract_id.id})
            if deduct:
                pricing -= adv_payment
        loan_amount = (pricing / float(mons)) * repetition
        m = 0
        i = 2
        while m < mons:
            loan_obj.create({'serial': i, 'amount': loan_amount, 'date': first_date, 'name': _('Loan Installment'),
                             'loan_id': self.contract_id.id})
            i += 1
            first_date = self.add_months(first_date, repetition)
            m += repetition
        return True

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def delete_insts(self):
        for line in self.installment_ids:
            if line.delete_ok:
                line.sudo().unlink()

    def check_insts_amount(self):
        total_amount = 0
        for line in self.installment_ids:
            if not line.delete_ok:
                total_amount += line.amount
        if self.total_amount != total_amount:
            raise exceptions.ValidationError(
                'Total Installment Amount Must Equal Unpaid installment Total Amount !')


class InstallmentsWizard(models.TransientModel):
    _name = 'installment.wizard'

    inst_id = fields.Many2one(comodel_name="loan.line.rs.own", string="Inst Id", required=False, )
    name = fields.Char('Name', required=True)
    date = fields.Date('Date', required=True)
    amount = fields.Float('Amount', digits=(16, 4), required=True)
    delete_ok = fields.Boolean('delete')
    rescheduling_id = fields.Many2one('installment.rescheduling')

    @api.multi
    def unlink(self):
        for line in self:
            if line.inst_id:
                line.inst_id.sudo().unlink()
        res = super(InstallmentsWizard, self).unlink()
        return res

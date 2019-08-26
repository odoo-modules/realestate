from datetime import datetime, timedelta
import time
import calendar
from odoo import api, fields, models, exceptions
from odoo.tools.translate import _
from datetime import datetime, date, timedelta as td
from odoo.exceptions import UserError


class ownership_contract(models.Model):
    _inherit = "ownership.contract"

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    reservation_amount = fields.Monetary(string="Reservation Payment", required=False, )

    def _prepare_lines(self, first_date):
        loan_lines = []
        if self.template_id:
            advance_percent = self.template_id.adv_payment_rate
            adv_payment = (self.pricing * float(advance_percent) / 100)
            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_('Please select first payment date!'))
            first_date = datetime.strptime(first_date, '%Y-%m-%d').date()
            if mon > 12:
                x = mon / 12
                mon = (x * 12) + mon % 12
            mons = mon + (yr * 12)
            pricing = self.pricing + ((self.template_id.rate / 100) * self.pricing)
            if adv_payment:
                loan_lines.append(
                    (0, 0, {
                        'serial': 1,
                        'amount': adv_payment - self.reservation_amount,
                        'due_amount': adv_payment - self.reservation_amount,
                        'date': first_date,
                        'name': _('Advance Payment'),
                    }))
                if deduct:
                    remain_amount = self.pricing - adv_payment
                    pricing = remain_amount + ((self.template_id.rate / 100) * remain_amount)
                else:
                    pricing = self.pricing + ((self.template_id.rate / 100) * self.pricing)
            loan_amount = (pricing / float(mons)) * repetition
            m = 0
            i = 2
            while m < mons:
                loan_lines.append(
                    (0, 0, {
                        'serial': i,
                        'amount': loan_amount,
                        'due_amount': loan_amount,
                        'date': first_date,
                        'name': _('Loan Installment')
                    }))
                i += 1
                first_date = self.add_months(first_date, repetition)
                m += repetition
        return loan_lines

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code = self.building_unit.code
        self.floor = self.building_unit.floor
        # self.pricing = self.building_unit.pricin
        self.type = self.building_unit.ptype
        self.address = self.building_unit.address
        self.status = self.building_unit.status
        self.building_area = self.building_unit.building_area

    pricing = fields.Integer('Price', compute="get_pricing", store=False)

    @api.depends('building_unit')
    def get_pricing(self):
        for line in self:
            if line.building_unit:
                line.pricing = line.building_unit.pricing

    def generate_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        account_move_obj = self.env['account.move']
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))

            for line in rec.loan_line:
                total += line.amount
            total += self.reservation_amount
            account_move_obj.create({'ref': rec.name, 'journal_id': journal.id,
                                     'line_ids': [(0, 0, {'name': rec.name,
                                                          'partner_id': rec.partner_id.id,
                                                          'account_id': rec.partner_id.property_account_receivable_id.id,
                                                          'analytic_account_id': rec.account_analytic_id.id,
                                                          'debit': total,
                                                          'credit': 0.0}),
                                                  (0, 0, {'name': rec.name,
                                                          'partner_id': rec.partner_id.id,
                                                          'account_id': rec.account_income.id,
                                                          'analytic_account_id': rec.account_analytic_id.id,
                                                          'debit': 0.0,
                                                          'credit': total})
                                                  ]})

    def generate_cancel_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))

            for line in rec.loan_line:
                total += line.amount
            total += self.reservation_amount

        account_move_obj = self.env['account.move']
        move_id = account_move_obj.create({'ref': self.name,
                                           'journal_id': journal.id,
                                           'line_ids': [(0, 0, {'name': self.name,
                                                                'account_id': self.partner_id.property_account_receivable_id.id,
                                                                'analytic_account_id': self.account_analytic_id.id,
                                                                'debit': 0.0,
                                                                'credit': total}),
                                                        (0, 0, {'name': self.name,
                                                                'account_id': self.account_income.id,
                                                                'analytic_account_id': self.account_analytic_id.id,
                                                                'debit': total,
                                                                'credit': 0.0})
                                                        ]
                                           })
        return move_id

    @api.depends('loan_line.amount', 'loan_line.paid')
    def _check_amounts(self):
        print("Hellllllllllllo")
        for rec in self:
            total_paid = 0
            total_nonpaid = 0
            total = self.reservation_amount
            for line in rec.loan_line:
                if line.paid:
                    total_paid += line.amount
                else:
                    total_nonpaid += line.amount
                total += line.amount
            rec.paid = total_paid
            rec.balance = total_nonpaid
            rec.total_amount = total

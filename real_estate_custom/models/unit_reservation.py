from odoo import api, fields, models, exceptions
import datetime
from datetime import datetime, date, timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare


class unit_reservation(models.Model):
    _inherit = "unit.reservation"

    expired_date = fields.Date(string="Cancel Reservation Date", required=False,
                               default=lambda res: datetime.today() + timedelta(days=1))

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    reservation_amount = fields.Monetary(string="Reservation Payment", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False)
    refund_voucher_id = fields.Many2one(comodel_name="account.voucher", string="Refund Voucher", required=False, )
    reservation_voucher_id = fields.Many2one(comodel_name="account.voucher", string="Reservation Voucher",
                                             required=False, context="{'voucher_type': 'sale'}")
    is_refunded = fields.Boolean(string="", default=False)
    building_area = fields.Float('Building Unit Area m2', related='building_unit.building_area')
    price_per_meter = fields.Monetary('Price Per Meter', related='building_unit.price_per_meter')

    @api.onchange('reservation_amount')
    def onchange_reservation_amount(self):
        if self.loan_line:
            advance_payment = self.loan_line.filtered(lambda line: line.name == 'Advance Payment')
            if advance_payment:
                pricing = self.pricing
                advance_percent = self.template_id.adv_payment_rate
                adv_payment = (pricing * float(advance_percent) / 100) - self.reservation_amount
                advance_payment.amount = adv_payment

    def action_refund(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reservation.refund',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': 'Reservation Amount Refund',
        }

    def action_confirm(self):
        if float_compare(self.reservation_amount, 0.0, precision_rounding=0.001) == 0:
            raise exceptions.ValidationError('Reservation Amount Must Be Geater Than Zero !')
        elif float_compare(self.reservation_amount, 0.0, precision_rounding=0.001) > 0:
            journal_id = self.journal_id
            if not journal_id:
                raise UserError(_('Please set sales accounting journal!'))
            voucher_obj = self.env['account.voucher']
            voucher_id = voucher_obj.create({'partner_id': self.partner_id.id,
                                             'real_estate_ref': self.name,
                                             'name': self.name,
                                             'account_id': journal_id.default_debit_account_id.id,
                                             'pay_now': 'pay_now',
                                             'reference': self.name,
                                             'voucher_type': 'sale',
                                             'journal_id': journal_id.id,
                                             })
            voucher_line_obj = self.env['account.voucher.line']
            voucher_line_obj.create(
                {
                    'voucher_id': voucher_id.id,
                    'name': "Reservation Payment",
                    'price_unit': self.reservation_amount,
                    'account_id': self.partner_id.property_account_receivable_id.id,
                    'account_analytic_id': self.account_analytic_id.id,
                })

            self.write({
                'state': 'confirmed',
                'reservation_voucher_id': voucher_id.id,
            })
            unit = self.building_unit
            unit.write({'state': 'reserved'})

    def action_contract(self):
        loan_lines = []
        if self.template_id:
            loan_lines = self._prepare_lines(self.date_payment)

        vals = {'building': self.building.id, 'country': self.country.id, 'city': self.city.id,
                'region': self.region.id,
                'reservation_amount': self.reservation_amount,
                'building_code': self.building_code, 'partner_id': self.partner_id.id,
                'building_unit': self.building_unit.id, 'unit_code': self.unit_code,
                'address': self.address, 'floor': self.floor, 'building_unit': self.building_unit.id,
                'pricing': self.pricing, 'date_payment': self.date_payment, 'template_id': self.template_id.id,
                'type': self.type.id, 'status': self.status.id, 'building_area': self.building_area,
                'account_analytic_id': self.account_analytic_id.id, 'reservation_id': self.ids[0],
                'account_income': self.account_income.id, 'loan_line': loan_lines}

        contract_obj = self.env['ownership.contract']
        contract_id = contract_obj.create(vals)
        self.write({'state': 'contracted'})
        self.write({'contract_id': contract_id.id})

        return {
            'name': _('Ownership Contract'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ownership.contract',
            'view_id': self.env.ref('itsys_real_estate.ownership_contract_form_view').id,
            'type': 'ir.actions.act_window',
            'res_id': contract_id.id,
            'target': 'current'
        }

    # awd
    @api.depends('contract_id')
    def _contract_count(self):
        self.contract_count = len(self.contract_id)

    contract_count = fields.Integer(compute='_contract_count', string='Contract Count', store=False)

    def _prepare_lines(self, first_date):
        loan_lines = []
        if self.template_id:
            # awd
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
                        'name': _('Advance Payment')
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
        print(self.pricing)
        self.unit_code = self.building_unit.code
        self.floor = self.building_unit.floor
        # self.pricing = self.building_unit.pricing
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

    @api.model
    def create(self, vals):
        print(vals.get('pricing'))
        new_record = super(unit_reservation, self).create(vals)
        return new_record

    def action_cancel_reservation(self):
        try:
            reservations = self.env['unit.reservation'].search(
                [('state', '=', 'confirmed'), ('expired_date', '<=', date.today())])
            for reservation in reservations:
                reservation.write({'state': 'canceled'})
                unit = reservation.building_unit
                unit.write({'state': 'free'})
        except Exception as e:
            raise exceptions.ValidationError(e.message)

# -*- coding: utf-8 -*- 
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
import time
import calendar
from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime, date,timedelta as td
from odoo.exceptions import UserError

class ownership_contract(models.Model):
    _name = "ownership.contract"
    _description = "Ownership Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.one
    @api.depends('loan_line.amount','loan_line.paid')
    def _check_amounts(self):
        total_paid = 0
        total_nonpaid = 0
        total=0
        for rec in self:
            for line in self.loan_line:
                if line.paid:
                    total_paid+= line.amount
                else:
                    total_nonpaid+= line.amount
                total+= line.amount

            rec.paid = total_paid
            rec.balance = total_nonpaid
            rec.total_amount = total

    def _voucher_count(self):
        voucher_obj = self.env['account.voucher']
        voucher_ids = voucher_obj.search([('real_estate_ref', '=', self.name)])
        self.voucher_count = len(voucher_ids)

    paid= fields.Float(compute='_check_amounts',string='Paid',store=True)
    balance= fields.Float(compute='_check_amounts',string='Balance',store=True)
    total_amount= fields.Float(compute='_check_amounts', string='Total Amount',store=True)
    #ownership_contract Info
    name= fields.Char    ('Name', size=64,readonly=True)
    reservation_id=  fields.Many2one('unit.reservation','Reservation')
    date= fields.Date    ('Date',required=True, default=fields.Date.context_today)
    date_payment= fields.Date    ('First Payment Date',required=True)
    #Building Info
    building= fields.Many2one('building','Building')
    building_code= fields.Char    ('Code', size=16)
    #Building Unit Info
    building_unit= fields.Many2one('product.template','Building Unit',domain=[('is_property', '=', True),('state', '=', 'free')],required=True)
    unit_code= fields.Char    ('Code', size=16)
    floor= fields.Char    ('Floor', size=16)
    address= fields.Char    ('Address')
    origin= fields.Char    ('Source Document')
    pricing= fields.Integer   ('Price', required=True)
    template_id= fields.Many2one('installment.template','Payment Template',required=True)
    type= fields.Many2one('building.type','Building Unit Type')
    status= fields.Many2one('building.status','Building Unit Status')
    city= fields.Many2one('cities','City')
    user_id= fields.Many2one('res.users','Responsible', default=lambda self: self.env.user,)
    partner_id= fields.Many2one('res.partner','Partner',required=True,domain=[('customer', '=', True)])
    building_area= fields.Integer ('Building Unit Area m²',)
    loan_line= fields.One2many('loan.line.rs.own', 'loan_id')
    region= fields.Many2one('regions','Region')
    country= fields.Many2one('countries','Country')
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('cancel','Canceled'),
                             ], 'State' , default='draft')

    voucher_count= fields.Integer('Voucher Count',compute='_voucher_count')

    account_income= fields.Many2one('account.account','Income Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_income_account.id if self.env['res.config.settings'].search([]) else "")
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).default_analytic_account.id if self.env['res.config.settings'].search([]) else "")

    @api.multi
    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete a contract not in draft state'))
        super(ownership_contract, self).unlink()

    def view_vouchers(self):
        vouchers=[]
        voucher_obj = self.env['account.voucher']
        voucher_ids = voucher_obj.search([('real_estate_ref', '=', self.name)])
        for obj in voucher_ids: vouchers.append(obj.id)

        return {
            'name': _('Receipts'),
            'domain': [('id', 'in', vouchers)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.voucher',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ownership.contract')
        new_id = super(ownership_contract, self).create(vals)
        return new_id

    def unit_status(self):
        return self.building_unit.state

    def action_confirm(self):
        unit = self.building_unit
        unit.write({'state': 'sold'})
        self.write({'state':'confirmed'})
        self.generate_entries()

    def action_cancel(self):
        unit = self.building_unit
        unit.write({'state':  'free'})
        self.generate_cancel_entries()
        self.write({'state':'cancel'})

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country:
            country_ids = self.env['cities'].search([('country_id', '=', self.country_id)])
            return {'domain': {'country': [('id', 'in', country_ids)]}}

    @api.onchange('city_id')
    def onchange_city(self):
        if self.city:
            region_ids = self.env['regions'].search([('city_id', '=', self.city_id)])
            return {'domain': {'region': [('id', 'in', region_ids)]}}

    @api.onchange('region_id')
    def onchange_region(self):
        if self.region:
            building_ids = self.env['building'].search([('region_id', '=', self.region_id)])
            return {'domain': {'building': [('id', 'in', building_ids)]}}

    @api.onchange('building_id')
    def onchange_building(self):
        if self.building:
            unit_ids = self.env['product.template'].search([('building_id', '=', self.building_id),('state','=','free')])
            building_obj = self.env['building'].browse(self.building.id)
            code =  building_obj.code
            if building_obj:
                return {'value': {'building_code': code}, 'domain': {'building_unit': [('id', 'in', unit_ids)]}}

    @api.onchange('template_id','date_payment','pricing')
    def onchange_tmpl(self):
        if self.template_id:
            loan_lines=self._prepare_lines(self.date_payment)
            self.loan_line= loan_lines

    def add_months(self,sourcedate,months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12 )
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return date(year,month,day)

    def _prepare_lines(self,first_date):
        loan_lines=[]
        if self.template_id:
            pricing = self.building_unit.pricing
            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            advance_percent = self.template_id.adv_payment_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_('Please select first payment date!'))
            first_date=datetime.strptime(first_date, '%Y-%m-%d').date()
            adv_payment=pricing*float(advance_percent)/100
            if mon>12:
                x = mon/12
                mon=(x*12)+mon%12
            mons=mon+(yr*12)
            if adv_payment:
                loan_lines.append((0,0,{'serial':1,'amount':adv_payment,'date': first_date, 'name':_('Advance Payment')}))
                if deduct:
                    pricing-=adv_payment
            loan_amount=(pricing/float(mons))*repetition
            m=0
            i=2
            while m<mons:
                loan_lines.append((0,0,{'serial':i,'amount':loan_amount,'date': first_date,'name':_('Loan Installment')}))
                i+=1
                first_date = self.add_months(first_date, repetition)
                m+=repetition
        return loan_lines

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code=self.building_unit.code
        self.floor=self.building_unit.floor
        self.pricing=self.building_unit.pricing
        self.type=self.building_unit.ptype
        self.address=self.building_unit.address
        self.status=self.building_unit.status
        self.building_area=self.building_unit.building_area

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        self.building =  self.reservation_id.building.id
        self.city =  self.reservation_id.city.id
        self.region =  self.reservation_id.region.id
        self.building_code =  self.reservation_id.building_code
        self.partner_id =  self.reservation_id.partner_id.id
        self.building_unit =  self.reservation_id.building_unit.id
        self.unit_code =  self.reservation_id.unit_code
        self.address =  self.reservation_id.address
        self.floor =  self.reservation_id.floor
        self.building_unit =  self.reservation_id.building_unit.id
        self.pricing =  self.reservation_id.pricing
        self.date_payment =  self.reservation_id.date_payment
        self.template_id =  self.reservation_id.template_id.id
        self.type =  self.reservation_id.type
        self.status =  self.reservation_id.status
        self.building_area =  self.reservation_id.building_area
        if self.template_id:
            loan_lines=self._prepare_lines(self.date_payment)
            self.loan_line= loan_lines

    def create_move(self,rec,debit,credit,move,account):
        move_line_obj = self.env['account.move.line']
        move_line_obj.create({
            'name': rec.name,
            'partner_id': rec.partner_id.id,
            'account_id': account,
            'debit': debit,
            'credit': credit,
            'move_id': move,
        })
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
                total+=line.amount
            account_move_obj.create({'ref' : rec.name, 'journal_id' : journal.id,
                                     'line_ids':[(0,0,{ 'name': rec.name,
                                                        'partner_id': rec.partner_id.id,
                                                        'account_id': rec.partner_id.property_account_receivable_id.id,'debit': total,
                                                        'credit': 0.0}),
                                                 (0,0,{'name': rec.name,
                                                       'partner_id': rec.partner_id.id,
                                                       'account_id': rec.account_income.id, 'debit': 0.0,
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
                total+=line.amount

        account_move_obj = self.env['account.move']
        move_id = account_move_obj.create({'ref': self.name,
                                           'journal_id': journal.id,
                                           'line_ids': [(0, 0, {'name': self.name,
                                                                'account_id': rec.partner_id.property_account_receivable_id.id,
                                                                'debit': 0.0,
                                                                'credit': total}),
                                                        (0, 0, {'name': self.name,
                                                                'account_id': rec.account_income.id,
                                                                'debit': total,
                                                                'credit': 0.0})
                                                        ]
                                           })
        return move_id

    def _prepare_lines(self,first_date):
        loan_lines=[]
        if self.template_id:
            pricing = self.building_unit.pricing
            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            advance_percent = self.template_id.adv_payment_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_('Please select first payment date!'))
            first_date=datetime.strptime(first_date, '%Y-%m-%d').date()
            adv_payment=pricing*float(advance_percent)/100
            if mon>12:
                x = mon/12
                mon=(x*12)+mon%12
            mons=mon+(yr*12)
            if adv_payment:
                loan_lines.append((0,0,{'serial':1,'amount':adv_payment,'date': first_date, 'name':_('Advance Payment')}))
                if deduct:
                    pricing-=adv_payment
            loan_amount=(pricing/float(mons))*repetition
            m=0
            i=2
            while m<mons:
                loan_lines.append((0,0,{'serial':i,'amount':loan_amount,'date': first_date,'name':_('Loan Installment')}))
                i+=1
                first_date = self.add_months(first_date, repetition)
                m+=repetition
        return loan_lines

class loan_line_rs_own(models.Model):
    _name = 'loan.line.rs.own'
    contract_user_id= fields.Many2one(string='User', related= 'loan_id.user_id', store=True)
    contract_partner_id= fields.Many2one(string='Partner', related= 'loan_id.partner_id', store=True)
    contract_building= fields.Many2one( string="Building", related='loan_id.building', store=True)
    contract_building_unit= fields.Many2one(related='loan_id.building_unit',string="Building Unit", store=True,domain=[('is_property', '=', True)])
    contract_city= fields.Many2one(related='loan_id.city',string="City", store=True)
    contract_region= fields.Many2one(related='loan_id.region',string="Region", store=True)
    contract_country= fields.Many2one(related='loan_id.country',string="Country", store=True)
    date= fields.Date('Due Date')
    name= fields.Char('Name')
    serial= fields.Char('#')
    empty_col= fields.Char(' ', readonly=True)
    amount= fields.Float('Payment', digits=(16, 4),)
    paid= fields.Boolean('Paid')
    loan_id= fields.Many2one('ownership.contract', '',ondelete='cascade', readonly=True)
    status= fields.Char('Status')
    company_id= fields.Many2one('res.company', readonly=True,  default=lambda self: self.env.user.company_id.id)


    @api.multi
    def send_multiple_installments(self):

        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('itsys_real_estate',
                                                         'email_template_installment_notification')[1]
        template_res = self.env['mail.template']
        template = template_res.browse(template_id)
        template.send_mail(self.id, force_send=True)
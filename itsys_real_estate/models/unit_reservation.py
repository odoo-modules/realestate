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
from odoo import api, fields, models
import datetime
from datetime import datetime, date,timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError

class unit_reservation(models.Model):
    _name = "unit.reservation"
    _description = "Property Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _contract_count(self):
        self.contract_count = len(self.contract_id)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team, oldname='section_id')
    account_income= fields.Many2one('account.account','Income Account')
    account_analytic_id= fields.Many2one('account.analytic.account','Analytic Account')
    contract_count= fields.Integer(compute='_contract_count', string='Contract Count',store=True)
    #Reservation Info
    name= fields.Char    ('Name', size=64, readonly=True)
    date= fields.Datetime    ('Date')
    date_payment= fields.Date    ('First Payment Date')
    #Building Info
    building= fields.Many2one('building','Building',)
    building_code= fields.Char    ('Code', size=16)
    #Building Unit Info
    building_unit= fields.Many2one('product.template','Building Unit',domain=[('is_property', '=', True),('state', '=', 'free')],required=True)
    unit_code= fields.Char    ('Code', size=16)
    floor= fields.Char    ('Floor', size=16)
    address= fields.Char    ('Address')
    pricing= fields.Integer   ('Price', required=True)
    template_id= fields.Many2one('installment.template','Payment Template',)
    contract_id= fields.Many2one('ownership.contract','Ownership Contract',)
    type= fields.Many2one('building.type','Building Unit Type',)
    status= fields.Many2one('building.status','Building Unit Status',)
    country= fields.Many2one('countries','Country',)
    city= fields.Many2one('cities','City',)
    region= fields.Many2one('regions','Region',)
    user_id= fields.Many2one('res.users','Responsible', default=lambda self: self.env.user,)
    partner_id= fields.Many2one('res.partner','Partner',domain=[('customer', '=', True)])
    building_area= fields.Integer ('Building Unit Area m²',)
    loan_line= fields.One2many('loan.line.rs', 'loan_id')
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('contracted','Contracted'),
                             ('canceled','Canceled')
                             ], 'State', default='draft')

    @api.multi
    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete a reservation not in draft state'))
        super(unit_reservation, self).unlink()
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Reservation Number record must be unique !')
    ]

    def auto_cancel_reservation(self):
        try:
            reservation_pool = self.env['unit.reservation']
            reservation_hours = self.env['res.config.settings'].browse(
                self.env['res.config.settings'].search([])[-1].id).default_reservation_hours if self.env[
                'res.config.settings'].search([]) else ""

            timeout_reservation_ids=reservation_pool.search([('state','=','confirmed'),('date','<=',str(datetime.now() - timedelta(hours=reservation_hours)))])
            for reservation in timeout_reservation_ids:
                reservation.write({'state': 'canceled'})
                unit = reservation.building_unit
                unit.write({'state': 'free'})
        except:
            return "internal error"

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code=self.building_unit.code
        self.floor=self.building_unit.floor
        self.pricing=self.building_unit.pricing
        self.type=self.building_unit.ptype
        self.address=self.building_unit.address
        self.status=self.building_unit.status
        self.building_area=self.building_unit.building_area

    def action_cancel(self):
        self.write({'state':'canceled'})
        unit = self.building_unit
        unit.write({'state':  'free'})

    def unit_status(self):
        return self.building_unit.state

    def action_confirm(self):
        self.write({'state':'confirmed'})
        unit = self.building_unit
        unit.write({'state': 'reserved'})

    def action_contract(self):
        loan_lines=[]
        if self.template_id:
            loan_lines = self._prepare_lines(self.date_payment)

        vals= {'building':self.building.id,'country':self.country.id, 'city':self.city.id, 'region':self.region.id,
               'building_code':self.building_code,'partner_id':self.partner_id.id,
               'building_unit':self.building_unit.id, 'unit_code':self.unit_code,
               'address':self.address,'floor':self.floor,'building_unit':self.building_unit.id,
               'pricing':self.pricing,'date_payment':self.date_payment,'template_id':self.template_id.id,
               'type':self.type.id,'status':self.status.id,'building_area':self.building_area,
               'account_analytic_id':self.account_analytic_id.id,'reservation_id':self.ids[0],
               'account_income':self.account_income.id,'loan_line':loan_lines}

        contract_obj = self.env['ownership.contract']
        contract_id = contract_obj.create(vals)
        self.write({'state':'contracted'})
        self.write({'contract_id':contract_id.id})

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


    def view_contract(self):
        for obj in self:
            contract_id = obj.contract_id.id
            return {
                'name': _('Ownership Contract'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ownership.contract',
                'view_id': self.env.ref('itsys_real_estate.ownership_contract_form_view').id,
                'type': 'ir.actions.act_window',
                'res_id': contract_id,
                'target': 'current'
            }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('unit.reservation')
        new_id = super(unit_reservation, self).create(vals)
        return new_id

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

    @api.onchange('template_id','date_payment','pricing')
    def onchange_tmpl(self):
        if self.template_id:
            loan_lines=self._prepare_lines(self.date_payment)
            self.loan_line= loan_lines

class loan_line_rs(models.Model):
    _name = 'loan.line.rs'
    _order = 'serial'

    date= fields.Date('Date')
    name= fields.Char('Name')
    serial= fields.Integer('#')
    empty_col= fields.Char(' ', readonly=True)
    amount= fields.Float('Payment', digits=(16, 4),)
    paid= fields.Boolean('Paid')
    contract_partner_id= fields.Many2one(related='loan_id.partner_id', string="Partner")
    contract_building= fields.Many2one(related='loan_id.building', string="Building")
    contract_building_unit= fields.Many2one(related='loan_id.building_unit', string="Building Unit")
    loan_id= fields.Many2one('unit.reservation', '',ondelete='cascade', readonly=True)

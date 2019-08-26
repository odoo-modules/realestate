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
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _

class unit_release(models.Model):
    _name = "unit.release"
    _description = "Property Release"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    #release Info
    name= fields.Char    ('Name', size=64, readonly=True)
    date= fields.Date    ('Date', required=True, default=fields.Date.context_today)
    date_payment= fields.Date    ('First Payment Date')
    #Building Info
    building= fields.Many2one('building','Building')
    building_code= fields.Char    ('Code', size=16)
    #Building Unit Info
    building_unit= fields.Many2one('product.template','Building Unit', domain=[('is_property', '=', True),('state', '=', 'free')])
    unit_code= fields.Char    ('Code', size=16)
    floor= fields.Char    ('Floor', size=16)
    address= fields.Char    ('Address')
    pricing= fields.Integer   ('Price',)
    template_id= fields.Many2one('installment.template','Payment Template')
    type= fields.Many2one('building.type','Building Unit Type')
    status= fields.Many2one('building.status','Building Unit Status')
    country_id= fields.Many2one('countries', string='Country', related='region_id.city_id.country_id', store=True, readonly=True)
    city= fields.Many2one('cities','City')
    region_id= fields.Many2one('regions','Region')
    user_id= fields.Many2one('res.users','Responsible', default=lambda self: self.env.user)
    partner_id1= fields.Many2one('res.partner','Partner', domain=[('customer', '=', True)], required=True)
    partner_id2= fields.Many2one('res.partner','Release to: ', domain=[('customer', '=', True)], required=True)
    contract_id= fields.Many2one('ownership.contract','Contract ', required=True, domain=[('state', '=', 'confirmed')])
    building_area= fields.Integer ('Building Unit Area m²',)
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('contracted','Contracted')
                             ], 'State', default= 'draft')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'release Number record must be unique !')
    ]

    @api.multi
    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete the release as it is not in draft state'))
        super(unit_release, self).unlink()
    def create_move(self,debit_acc,credit_acc,partner,journal):
        account_move_obj = self.env['account.move']
        move_id = account_move_obj.create({'ref': self.name,
                                           'journal_id': journal,
                                           'line_ids':[(0,0,{ 'name': self.name,
                                                              'partner_id': partner,
                                                              'account_id': debit_acc,
                                                              'debit':self.contract_id.paid,
                                                              'credit': 0.0}),
                                                       (0, 0, {'name': self.name,
                                                               'partner_id': self.partner_id1.id,
                                                               'account_id': credit_acc,
                                                               'debit': 0.0,
                                                               'credit': self.contract_id.paid})
                                                       ]
                                           })
        return move_id

    def action_confirm(self):
        journal_pool = self.env['account.journal']
        cash_journal = journal_pool.search([('type', '=', 'cash')], limit=1)
        refund_journal = journal_pool.search([('type', '=', 'sale')], limit=1)

        if not refund_journal:
            raise UserError(_('Please set sale refund journal!'))

        if not cash_journal:
            raise UserError(_('Please set cash journal!'))

        refund_account=refund_journal.default_debit_account_id.id
        cash_account=cash_journal.default_debit_account_id.id

        self.create_move(refund_account, self.partner_id1.property_account_receivable_id.id, self.partner_id1.id, refund_journal.id)
        self.create_move(self.partner_id1.property_account_receivable_id.id, cash_account , self.partner_id1.id, cash_journal.id)
        self.create_move(cash_account ,self.partner_id2.property_account_receivable_id.id, self.partner_id2.id, cash_journal.id)
        self.write({'state':'confirmed'})

    def action_contract(self):
        for release_unit_obj in self:
            contract_obj = self.env['ownership.contract']
            contract_id = release_unit_obj.contract_id.id
            contract_obj = contract_obj.browse(contract_id)
            building =  contract_obj.building.id
            origin = contract_obj.name
            city =  contract_obj.city.id
            region =  contract_obj.region.id
            code_building =  contract_obj.building_code
            partner =  release_unit_obj.partner_id2.id
            unit_building =  contract_obj.building_unit.id
            code =  contract_obj.unit_code
            address =  contract_obj.address
            floor =  contract_obj.floor
            unit_id =  contract_obj.building_unit.id
            pricing =  contract_obj.pricing
            date_payment =  contract_obj.date_payment
            template_id =  contract_obj.template_id.id
            type =  contract_obj.type.id
            status =  contract_obj.status.id
            building_area =  contract_obj.building_area
            account_analytic_id =  contract_obj.account_analytic_id.id
            account_income =  contract_obj.account_income.id
            loan_lines=[]
            for line in contract_obj.loan_line:
                #if not line.paid:
                loan_lines.append((0,0,{'paid': line.paid, 'serial':line.serial,'amount':line.amount,'date': line.date,'name':line.name}))
            vals= {'origin':origin,'template_id':template_id,'building':building,'city':city,'building_code':code_building,
                   'partner_id':partner,'date_payment':date_payment,'account_income':account_income,'account_analytic_id':account_analytic_id,
                   'building_unit':unit_building,'loan_line':loan_lines,'unit_code': code,'floor': floor,'pricing': pricing,
                   'region':region, 'type': type,'address': address,'status': status,'building_area': building_area}
            contract_obj = self.env['ownership.contract']
            contract_id = contract_obj.create(vals)
            self.write({'state':'contracted'})
            mod_obj = self.env['ir.model.data']
            res = mod_obj.get_object_reference('itsys_real_estate', 'ownership_contract_form_view')
            res_id = res and res[1] or False
            self.write({'contract_id':contract_id.id})
            return {
                'view_type':  'form',
                'view_mode':  'form',
                'view_id':  [res_id],
                'res_model':  'ownership.contract',
                'type':  'ir.actions.act_window',
                'nodestroy':  True,
                'target':  'current',
                'res_id':  contract_id.id,
            }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('unit.release')
        new_id = super(unit_release, self).create(vals)
        return new_id

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country:
            country_ids = self.env['cities'].search([('country_id', '=', self.country_id)])
            return {'domain': {'country': [('id', 'in', country_ids)]}}

    @api.onchange('city')
    def onchange_city(self):
        if self.city:
            region_ids = self.env['regions'].search([('city_id', '=', self.city.id)])
            return {'domain': {'region': [('id', 'in', region_ids)]}}

    @api.onchange('region_id')
    def onchange_region(self):
        if self.region_id:
            building_ids = self.env['building'].search([('region_id', '=', self.region_id.id)])
            return {'domain': {'building': [('id', 'in', building_ids)]}}

    @api.onchange('building')
    def onchange_building(self):
        if self.building:
            unit_ids = self.env['product.template'].search([('is_property', '=', True),('building_id', '=', self.building.id),('state','=','free')])
            building_obj = self.env['building'].browse(self.building.id)
            code =  building_obj.code
            if building_obj:
                return {'value': {'building_code': code}, 'domain': {'building_unit': [('id', 'in', unit_ids)]}}

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code = self.building_unit.code
        self.floor = self.building_unit.floor
        self.pricing = self.building_unit.pricing
        self.type = self.building_unit.ptype
        self.address = self.building_unit.address
        self.status = self.building_unit.status
        self.building_area = self.building_unit.building_area

    @api.onchange('contract_id')
    def onchange_contract(self):
        if self.contract_id:
            contract_obj = self.env['ownership.contract'].browse(self.contract_id.id)
            self.building =  contract_obj.building.id
            self.city =  contract_obj.city.id
            self.region_id =  contract_obj.region.id
            self.building_code =  contract_obj.building_code
            self.partner_id1 =  contract_obj.partner_id.id
            self.building_unit =  contract_obj.building_unit.id
            self.unit_code =  contract_obj.unit_code
            self.address =  contract_obj.address
            self.floor =  contract_obj.floor
            self.building_unit =  contract_obj.building_unit.id
            self.pricing =  contract_obj.pricing
            self.type =  contract_obj.type.id
            self.status =  contract_obj.status
            self.building_area =  contract_obj.building_area

    _sql_constraints = [
        ('same_partner', 'CHECK(partner_id1!=partner_id2)','Error ! Can not release to same partner')

    ]

# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class report_ownership_contract_bi(models.Model):
    _name = "report.ownership.contract.bi"
    _description = "Ownership Contracts Statistics"
    _auto = False

    contract_date= fields.Date('Contract Date', readonly=True)
    due_date= fields.Date('Due Date', readonly=True)
    name= fields.Char('Contract', readonly=True)
    partner_id= fields.Many2one('res.partner', 'Partner', readonly=True)
    user_id=fields.Many2one('res.users', 'Responsible', readonly=True)
    contract_unit= fields.Many2one('product.template', 'Property', readonly=True)
    contract_country= fields.Many2one('countries', 'Country', readonly=True)
    contract_city= fields.Many2one('cities', 'City', readonly=True)
    contract_building= fields.Many2one('building', 'Building', readonly=True)
    contract_region= fields.Many2one('regions', 'Region', readonly=True)
    paid= fields.Float('Paid Amount', readonly=True)
    unpaid= fields.Float('Balance', readonly=True)
    amount= fields.Float('Amount', digits=(16, 4), readonly=True)
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('cancel','Canceled'),
                             ], 'State')

    _order = 'contract_date desc'
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_ownership_contract_bi')
        self._cr.execute("""
            create or replace view report_ownership_contract_bi as (
                select min(lro.id) as id,
                oc.name, 
                oc.date as contract_date, 
                oc.partner_id as partner_id, 
                oc.building_unit as contract_unit, 
                oc.building as contract_building,
                oc.country as contract_country, 
                oc.state as state,
                oc.city as contract_city, oc.region as contract_region, 
                lro.date as due_date,
		oc.user_id as user_id,
                CASE WHEN lro.paid=True
                THEN lro.amount
                ELSE 0.0
                END as paid, 
                CASE WHEN lro.paid=False
                THEN lro.amount
                ELSE 0.0            
                END as unpaid,	    
                lro.amount as amount
                FROM loan_line_rs_own lro
                LEFT JOIN ownership_contract oc ON oc.id = lro.loan_id
                GROUP BY
                    oc.state,
                    lro.paid, 
                    lro.amount, 
                    oc.name, 
                    oc.partner_id, 
                    oc.building_unit, 
                    oc.building, 
                    oc.country, 
                    oc.city, 
                    oc.region, 
                    oc.date, 
                    lro.date,
                    oc.user_id           
           )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
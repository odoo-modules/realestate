# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2011 odoo S.A (<http://www.odoo.com>).
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

import logging
#from nexmomessage import NexmoMessage
from odoo import api, fields, models 
from odoo.tools.translate import _
from odoo.tools import email_split
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)

class sms_wizard(models.TransientModel):
    _name = 'sms.wizard'
    
    def action_apply(self):
        loans=self.env['loan.line.rs.own'].browse(context.get('active_ids', [])) 
        sms_conf = self.env['sms']
        sms_conf_ids = sms_conf.search( [], limit=1, order='id desc')        
        sms_conf_obj=sms_conf.browse(sms_conf_ids)
        sms_text=sms_conf_obj.name
        for loan in loans:
            if not loan.contract_partner_id.mobile:
                raise UserError(_('Please set partner mobile number!'))

            values = {"partner": loan.contract_partner_id.name
                       ,"date": loan.date or None
                       ,"amount": round(loan.amount,2) or 0.0
                       ,"contract": loan.contract or ''
                       ,"building": loan.contract_building.name or None
                       ,"unit": loan.contract_building_unit.name or None
                        }
            x= sms_text.format(**values)
            msg ={
                'reqtype': 'json',
                'api_key': 'eab846b9' ,
                'api_secret': '540380c7' ,
                'from': '00201007394256' ,
                'to': '002'+loan.contract_partner_id.mobile,
                'text': x ,
                }

            sms = NexmoMessage(msg)
            sms.set_text_info(msg['text'])

            sms.send_request()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

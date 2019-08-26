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

class mail_wizard(models.TransientModel):
    _name = 'mail.wizard'
    
    def action_apply(self):
        message_obj = self.env['mail.message']
        mail_obj = self.env['mail.mail']
        mail_ids = []
        mail_body=''
        email_crash_flag = 1
        loans=self.env['loan.line.rs.own'].browse(context.get('active_ids', [])) 
        mail_conf = self.env['mail']
        mail_conf_ids = mail_conf.search( [], limit=1, order='id desc')        
        mail_conf_obj=mail_conf.browse(mail_conf_ids)
        mail_text=mail_conf_obj.mail
        mail_subject=mail_conf_obj.name
        for loan in loans:
            values = {"partner": loan.contract_partner_id.name
                       ,"date": loan.date or None
                       ,"amount": round(loan.amount,2) or 0.0
                       ,"contract": loan.loan_id or ''
                       ,"building": loan.contract_building.name or None
                       ,"unit": loan.contract_building_unit.name or None
                        }
            if not mail_text:
                raise UserError(_('Please set email format! '))                
            mail_body= mail_text.format(**values)
            if not loan.contract_partner_id.email:
                raise UserError(_('Please Provide Email for recepients! '))
            mail_to = loan.contract_partner_id.email 
            reply_to = 'noreply@admin.com' 
            #if not mail_to: 
            #    continue
            # ----- Create relative message (required by mail)
            message_id = message_obj.create({
                    'type' : 'email',
                    'subject' : mail_subject,
            })
            # ----- Create mail
            mail_id = mail_obj.create({
                    'mail_message_id' : message_id,
                    'state' : 'outgoing',
                    'email_to' : mail_to,
                    'reply_to' : reply_to,
                    'body_html' : mail_body,
            })
            mail_ids = [mail_id,]
            if not mail_ids:
                return False
            email_sent = mail_obj.send(mail_ids)
            if email_sent:
                email_crash_flag = 0
        return True



class mail_wizard_rent(models.TransientModel):
    _name = 'mail.wizard.rent'
    
    def action_apply(self):
        message_obj = self.env['mail.message']
        mail_obj = self.env['mail.mail']
        mail_ids = []
        mail_body=''
        email_crash_flag = 1
        loans=self.env['loan.line.rs.rent'].browse(context.get('active_ids', [])) 
        mail_conf = self.env['mail']
        mail_conf_ids = mail_conf.search( [], limit=1, order='id desc')        
        mail_conf_obj=mail_conf.browse(mail_conf_ids)
        mail_text=mail_conf_obj.mail
        mail_subject=mail_conf_obj.name
        for loan in loans:
            values = {"partner": loan.contract_partner_id.name
                       ,"date": loan.date or None
                       ,"amount": round(loan.amount,2) or 0.0
                       ,"contract": loan.loan_id or ''
                       ,"building": loan.contract_building.name or None
                       ,"unit": loan.contract_building_unit.name or None
                        }
            if not mail_text:
                raise UserError(_('Please set email format! '))                
            x= mail_text.format(**values)
            if not loan.contract_partner_id.email:
                raise UserError(_('Please Provide Email for recepients! '))
            mail_to = loan.contract_partner_id.email 
            reply_to = 'noreply@admin.com' 
            message_id = message_obj.create({
                    'type' : 'email',
                    'subject' : mail_subject,
            })
            # ----- Create mail
            mail_id = mail_obj.create({
                    'mail_message_id' : message_id,
                    'state' : 'outgoing',
                    'email_to' : mail_to,
                    'reply_to' : reply_to,
                    'body_html' : x,
            })
            mail_ids = [mail_id,]
            if not mail_ids:
                return False
            email_sent = mail_obj.send(mail_ids)
            if email_sent:
                email_crash_flag = 0
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta
import sys

class account_bank_statement(models.Model):
    _inherit = "account.bank.statement"    
    real_estate_ref= fields.Char('Real Estate Ref.', )
   

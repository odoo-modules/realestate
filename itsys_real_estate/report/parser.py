# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with odoo SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Parser(models.AbstractModel):
    def __init__(self, name, context):
        super(self.__class__, self).__init__(name, context)
        self.localcontext.update({
            'hello_world':self.hello_world,
            'get_day':self._get_day,
            'get_day_r':self._get_day_r,
            'convert':self.convert,
            'get_day_contract':self._get_day_contract,
	    'localize_date':self.localize_date,  
	    'localize_number':self.localize_number,  
        })

    def convert(self, amount, cur):
    	return tafqeet.DITAFQEET( amount )

    def localize_number(self, number):
        num_lst=list(str(number))
        i=0
        num_len=len(list(str(number)))
        while i< num_len:
            if num_lst[i]=="0":
                num_lst[i]="٠"
            if num_lst[i]=="1":
                num_lst[i]="١"
            if num_lst[i]=="2":
                num_lst[i]="٢"
            if num_lst[i]=="3":
                num_lst[i]="٣"
            if num_lst[i]=="4":
                num_lst[i]="٤"
            if num_lst[i]=="5":
                num_lst[i]="٥"
            if num_lst[i]=="6":
                num_lst[i]="٦"
            if num_lst[i]=="7":
                num_lst[i]="٧"
            if num_lst[i]=="8":
                num_lst[i]="٨"
            if num_lst[i]=="9":
                num_lst[i]="٩"
            i+=1
        return "".join(num_lst)

    def localize_date(self, number):
        if number:
            num_lst=list(str((number)))
            i=0
            num_len=len(list(str(number)))
            while i< num_len:
                if num_lst[i]=="0":
                    num_lst[i]="٠"
                if num_lst[i]=="1":
                    num_lst[i]="١"
                if num_lst[i]=="2":
                    num_lst[i]="٢"
                if num_lst[i]=="3":
                    num_lst[i]="٣"
                if num_lst[i]=="4":
                    num_lst[i]="٤"
                if num_lst[i]=="5":
                    num_lst[i]="٥"
                if num_lst[i]=="6":
                    num_lst[i]="٦"
                if num_lst[i]=="7":
                    num_lst[i]="٧"
                if num_lst[i]=="8":
                    num_lst[i]="٨"
                if num_lst[i]=="9":
                    num_lst[i]="٩"
                i+=1
            tokens = ("".join(num_lst)).split("-")
            return tokens[2]+"-"+tokens[1]+"-"+tokens[0]

    def hello_world(self, name):
        return "Hello, %s!" % name

    def _get_day(self,d):
        if d=='False':
            return ''    
        ar_day=""      
        x = datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%A')
        if x == "Monday":
            ar_day="اﻻثنين"
        if x == "Saturday":
            ar_day="السبت"
        if x == "Sunday":
            ar_day="اﻻحــــد"
        if x == "Tuesday":
            ar_day="الثلاثاء"
        if x == "Thursday":
            ar_day="الخميس"
        if x == "Friday":
            ar_day="الجمعة"
        if x == "Wednesday":
            ar_day="اﻻربعاء"
        return ar_day

    def _get_day_r(self,d):
        if d=='False':
            return ''    
        ar_day=""      
        x = datetime.strptime(d, '%Y-%m-%d').strftime('%A')
        if x == "Monday":
            ar_day="اﻻثنين"
        if x == "Saturday":
            ar_day="السبت"
        if x == "Sunday":
            ar_day="اﻻحــــد"
        if x == "Tuesday":
            ar_day="الثلاثاء"
        if x == "Thursday":
            ar_day="الخميس"
        if x == "Friday":
            ar_day="الجمعة"
        if x == "Wednesday":
            ar_day="اﻻربعاء"
        return ar_day

    def _get_day_contract(self,d):
        if d=='False':
            return ''    
        ar_day=""      
        x = datetime.strptime(d, '%Y-%m-%d').strftime('%A')
        if x == "Monday":
            ar_day="اﻻثنين"
        if x == "Saturday":
            ar_day="السبت"
        if x == "Sunday":
            ar_day="اﻻحــــد"
        if x == "Tuesday":
            ar_day="الثلاثاء"
        if x == "Thursday":
            ar_day="الخميس"
        if x == "Friday":
            ar_day="الجمعة"
        if x == "Wednesday":
            ar_day="اﻻربعاء"
        return ar_day


    @api.model
    def get_report_values(self, docids, data=None):
        return {
            'get_day': self._get_day,
            'get_day_r': self._get_day_r,
            'convert': self.convert,
            'get_day_contract': self._get_day_contract,
            'localize_date': self.localize_date,
            'localize_number': self.localize_number,


            'get_header_info': self._get_header_info(data['form']['date_from'], data['form']['holiday_type']),
            'get_day': self._get_day(data['form']['date_from']),
            'get_months': self._get_months(data['form']['date_from']),
            'get_data_from_report': self._get_data_from_report(data['form']),
            'get_holidays_status': self._get_holidays_status(),
        }
        return {'lines': res}

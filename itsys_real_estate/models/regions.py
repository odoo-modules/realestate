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
from odoo.tools.translate import _
from odoo import api, fields, models 

class regions(models.Model):
    _name = "regions"
    _description = "Region"
    _parent_name = "region_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    _rec_name = 'complete_name'
    _inherit = ['mail.thread']

    @api.one
    @api.depends('name', 'region_id')
    def _compute_complete_name(self):
        """ Forms complete name of region from region to child region. """
        name = self.name
        current = self
        while current.region_id:
            current = current.region_id
            name = '%s/%s' % (current.name, name)
        self.complete_name = name


    @api.one
    @api.depends('name', 'region_id.complete_name')
    def _compute_complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.region_id.complete_name:
            self.complete_name = '%s/%s' % (self.region_id.complete_name, self.name)
        else:
            self.complete_name = self.name

    name= fields.Char ('Name',required=True)
    complete_name = fields.Char("Full Name", compute='_compute_complete_name', store=True)
    child_ids= fields.One2many('regions', 'region_id', 'Contains')
    parent_left= fields.Integer('Left Parent', index=True)
    parent_right= fields.Integer('Right Parent', index=True)
    account= fields.Many2one('account.account','Discount Account', )
    account_me= fields.Many2one('account.account','Managerial Expenses Account', )
    #map= fields.html('Map', help='Automatically sanitized HTML contents')
    city_id= fields.Many2one('cities','City', )
    country_id= fields.Many2one('countries', string='Country', related='city_id.country_id', store=True, readonly=True)
    region_id= fields.Many2one('regions','Parent Region', ondelete='cascade')
       

    def unit_status(self, unit_id):
        self.env.cr.execute("select state from building_unit where id = "+str(int(unit_id)))
        res = self.env.cr.dictfetchone()
        if res:
            if res["state"]:
                return res["state"]
    """
    def update_map(self, region_id, map):
        #res = self.unit_region(ids, unit_id)
        #region_id = res["region"]
        #map = res["map"]
        region_pool=self.env["regions"]
        #map = region_pool.browse(cr,uid,region_id).map
        updated_map=""
        if region_id and map:
            map_parts = map.split("<!--separator-->")
            header_pins = map_parts[0]
            map_image = map_parts[1]
            map_key = map_parts[2]
            map_lines = map_image.splitlines()
            final_header_pins = ""
            #raise UserError(_(map_lines))
            for line in map_lines:
                coords = []
                status = None
                unit_id = None
                if line[:5] == '<area=                 
                    line_parts = line.split(" ")
                    for part in line_parts:                        
                        if part[:6]=="coords":
                            t = part.split("=")[1]
                            coords = t.split(",")
                            coords[0].replace('"','')
                            coords = [coords[0][1:],coords[1]]
                        if part[:4]=="href":                             
                            unit_id = ((part.split("#")[1]).split("&")[0]).split("=")[1]
                            status = self.unit_status(ids, int(unit_id))
                if len(coords)>0 and status:
                    header_line=""
                    if status == 'free':
                        style='top: '+str(coords[1])+'px; left: '+str(coords[0])+'px;font-size: 15px;position: absolute; color: green;'
                    if status == 'reserved':
                        style="top: "+str(coords[1])+"px; left: "+str(coords[0])+"px;font-size: 15px;position: absolute; color: blue;"
                    if status == 'sold':
                        style='top: '+str(coords[1])+'px; left: '+str(coords[0])+'px;font-size: 15px;position: absolute; color: red;'
                    header_line = '<div style="' +str(style)+'">◆</div>'
                    final_header_pins+=header_line
                    final_header_pins+="\n"
            updated_map = final_header_pins + "<!--separator-->" + map_image + "<!--separator-->"+ map_key
            return updated_map
            #self.env.cr.execute("update regions set map='"+str(updated_map)+"' where id="+str(region_id))
            #proj_pool= self.env["regions")
            #proj_obj= proj_pool.browse(cr,uid,region_id)
            #proj_obj.write({'map= updated_map})
            #proj_pool.write([region_id], {'map= updated_map}, context)
            #raise UserError(_(updated_map))
                                                    
    @api.model    
    def create(self, vals):
        map_parts = vals['map'].split("<!--separator-->")   
        if len(map_parts)!=3:
            raise UserError(_('Invalid map format'))
        return super(regions, self).create(vals)


    def write(self, vals):
        if vals:
	    if vals['map']:
		    map_parts = vals['map'].split("<!--separator-->")   
		    if len(map_parts)!=3:
		        raise UserError(_('Invalid map format'))
		    vals['map'] = self.update_map(ids, ids[0],vals['map'])
            #raise UserError(_(vals['map']))
        return super(regions, self).write(ids, vals)
    """

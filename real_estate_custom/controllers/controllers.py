# -*- coding: utf-8 -*-
from odoo import http

# class RealEstateCustom(http.Controller):
#     @http.route('/real_estate_custom/real_estate_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_estate_custom/real_estate_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_estate_custom.listing', {
#             'root': '/real_estate_custom/real_estate_custom',
#             'objects': http.request.env['real_estate_custom.real_estate_custom'].search([]),
#         })

#     @http.route('/real_estate_custom/real_estate_custom/objects/<model("real_estate_custom.real_estate_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_estate_custom.object', {
#             'object': obj
#         })
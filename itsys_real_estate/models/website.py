# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_property_domain(self):
        return [("is_property", "=", True),("website_published","=",True)]

    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom'),
    ], default='left',
        string='Thumbnails panel position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(
        string='Play interval of slideshow',
        default='5000',
        help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(
        string='Enable the text panel',
        default=True,
        help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur'), ],
        default='default',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(
        string='Slider effects',
        default=True,
        help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(string="Change thumbnail size", default=False)
    thumb_height = fields.Char(string='Thumb height', default=50)
    thumb_width = fields.Char(string='Thumb width', default=88)

    @api.multi
    def get_multiple_images(self, product_id=None):

        productsss = False
        if product_id:
            products = self.env['biztech.product.images'].search(
                [('product_tmpl_id', '=', product_id), ('more_view_exclude', '=', False)], order='sequence')
            if products:
                return products
        return productsss
        

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom')],
        string='Thumbnails panel position',
        related='website_id.thumbnail_panel_position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(
        string='Play interval of slideshow',
        related='website_id.interval_play',
        help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(
        string='Enable the text panel',
        related='website_id.enable_disable_text',
        help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur')],
        related='website_id.color_opt_thumbnail',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(
        string='Slider effects',
        # default=True,
        related='website_id.no_extra_options',
        help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(
        string="Change thumbnail size",
        related="website_id.change_thumbnail_size")
    thumb_height = fields.Char(
        string='Thumb height',
        related="website_id.thumb_height")
    thumb_width = fields.Char(
        string='Thumb width',
        related="website_id.thumb_width")
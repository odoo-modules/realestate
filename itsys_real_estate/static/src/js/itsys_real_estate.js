odoo.define('website_multiple_product_image_effect.multi_img_effect', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {

        var api;
        ajax.jsonRpc('/product/image_effect_config', 'call', {})
            .done(function(res) {

                var dynamic_data = {}
                dynamic_data['gallery_images_preload_type'] = 'all'
                dynamic_data['slider_enable_text_panel'] = false
                dynamic_data['gallery_skin'] = "alexis"

                if (res.theme_panel_position != false) {
                    dynamic_data['theme_panel_position'] = res.theme_panel_position
                }

                if (res.interval_play != false) {
                    dynamic_data['gallery_play_interval'] = res.interval_play
                }

                if (res.color_opt_thumbnail != false && res.color_opt_thumbnail != 'default') {
                    dynamic_data['thumb_image_overlay_effect'] = true
                    if (res.color_opt_thumbnail == 'b_n_w') {}
                    if (res.color_opt_thumbnail == 'blur') {
                        dynamic_data['thumb_image_overlay_type'] = "blur"
                    }
                    if (res.color_opt_thumbnail == 'sepia') {
                        dynamic_data['thumb_image_overlay_type'] = "sepia"
                    }
                }

                if (res.enable_disable_text == true) {
                    dynamic_data['slider_enable_text_panel'] = true
                }

                if (res.change_thumbnail_size == true) {
                    dynamic_data['thumb_height'] = res.thumb_height
                    dynamic_data['thumb_width'] = res.thumb_width
                }

                if (res.no_extra_options == false) {
                    dynamic_data['slider_enable_arrows'] = false
                    dynamic_data['slider_enable_progress_indicator'] = false
                    dynamic_data['slider_enable_play_button'] = false
                    dynamic_data['slider_enable_fullscreen_button'] = false
                    dynamic_data['slider_enable_zoom_panel'] = false
                    dynamic_data['slider_enable_text_panel'] = false
                    dynamic_data['strippanel_enable_handle'] = false
                    dynamic_data['gridpanel_enable_handle'] = false
                    dynamic_data['theme_panel_position'] = 'bottom'
                    dynamic_data['thumb_image_overlay_effect'] = false
                }

                api = $('#gallery').unitegallery(dynamic_data);
                api.on("item_change", function(num, data) {
                    if (data['index'] == 0) {
                        update_gallery_product_image();
                    }
                });

                if (api != undefined && $('#gallery').length != 0){
                    setTimeout(function(){
                        update_gallery_product_image()
                    }, 500);
                }
            });
        function update_gallery_product_image() {
            var $container = $('.oe_website_sale').find('.ug-slide-wrapper');
            var $img = $container.find('img');
            var $product_container = $('.oe_website_sale').find('.js_product').first();
            var p_id = parseInt($product_container.find('input.product_id').first().val());

            if (p_id > 0) {
                $img.each(function(e_img) {
                    if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                        $(this).attr("src", "/web/image/product.product/" + p_id + "/image");
                    }
                });
            } else {
                var spare_link = api.getItem(0).urlThumb;
                $img.each(function(e_img) {
                    if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                        $(this).attr("src", spare_link);
                    }
                });
            }
        }

        function update_gallery_product_variant_image(event_source, product_id) {
            var $imgs = $(event_source).closest('.oe_website_sale').find('.ug-slide-wrapper');
            var $img = $imgs.find('img');
            var total_img = api.getNumItems()
            if (total_img != undefined) {
                api.selectItem(0);
            }
            var $stay;
            $img.each(function(e) {
                if ($(this).attr("src").startsWith('/web/image/biztech.product.images/') == false) {
                    $(this).attr("src", "/web/image/product.product/" + product_id + "/image");

                    $stay = $(this).parent().parent();
                    $(this).css({
                        'width': 'initial',
                        'height': 'initial'
                    });
                    api.resetZoom();
                    api.zoomIn();
                }
            });
        }
        
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            $(oe_website_sale).on('change', 'input.js_product_change', function () {
                var self = this;
                var $parent = $(this).closest('.js_product');
                update_gallery_product_variant_image(this, +$(this).val());
            });
            
            $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function(ev) {
                if (api != undefined){
                    var $ul = $(ev.target).closest('.js_add_cart_variants');
                    var $parent = $ul.closest('.js_product');
                    var variant_ids = $ul.data("attribute_value_ids");
                    var values = [];                 
                    if(_.isString(variant_ids)) {
                        variant_ids = JSON.parse(variant_ids.replace(/'/g, '"'));
                    }
                    var unchanged_values = $parent.find('div.oe_unchanged_value_ids').data('unchanged_value_ids') || [];
                    $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                        values.push(+$(this).val());
                    });
                    values =  values.concat(unchanged_values);

                    var product_id = false;
                    for (var k in variant_ids) {
                        if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                            product_id = variant_ids[k][0];
                            update_gallery_product_variant_image(this, product_id);
                            break;
                        }
                    }
                }
            });
        });
    });
});



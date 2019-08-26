/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('itsys_real_estate.init', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    //default key
    var default_key = 'AIzaSyAu47j0jBPU_4FmzkjA3xc_EKoOISrAJpI';

    rpc.query({
        model: 'gmap.config',
        method: 'get_key_api',
        args: []
    }).then(function (key) {
        if (!key) {
            key = default_key;
        }
        $.getScript('http://maps.googleapis.com/maps/api/js?key=' + key + '&libraries=places');
    });
});
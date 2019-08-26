/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('itsys_real_estate.place_autocomplete_multi', function(require){

    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    var MapWidget = require('itsys_real_estate.map_widget_multi');


    var place_autocomplete_multi = basic_fields.FieldChar.extend({
        init: function(parent, name, record, options){


            this._super.apply(this, arguments);
            if (parent.state.data.latlng_ids.data.length>0){
                this.lat = parent.state.data.latlng_ids.data[0].data.lat;
                this.lng = parent.state.data.latlng_ids.data[0].data.lng;
            console.log(parent.state.data.latlng_ids.data[0].data.lat)
            console.log(parent.state.data.latlng_ids.data[0].data.lng)
            console.log('parenttttttttttttttttttttttttttttt')
            }
            else {
                this.lat = 30.04300466950456;
                this.lng = 31.235621482518354;
            }
        },
        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.t = setInterval(function () {
                    if (typeof google != 'undefined') {
                        self.on_ready();
                    }
                }, 1000);
            });
        },
        on_ready: function(){
            var self = this;

            if(self.t){
                clearInterval(self.t);
            }

            if (!self.$input) {
                return;
            }

            var map_widget = new MapWidget(self);
            map_widget.insertAfter(self.$input);

            // init gmap marker position
            var geocoder = new google.maps.Geocoder;
            geocoder.geocode({'address': self.$input.val()}, function (results, status) {
                if (status === 'OK') {
                    self.lat = results[0].geometry.location.lat();
                    self.lng = results[0].geometry.location.lng();
                    map_widget.lat = self.lat;
                    map_widget.lng = self.lng;
                }
            });

            var autocomplete = new google.maps.places.Autocomplete((self.$input[0]), {types: ['geocode']});

            autocomplete.addListener('place_changed', function (){
                var place = autocomplete.getPlace();

                if(!place.geometry || !place.geometry.location){
                    return;
                }

                var location = place.geometry.location;
                self.lat = location.lat();
                self.lng = location.lng();
                // update gmap
                map_widget.update_marker(self.lat, self.lng);
            });

        },
        update_place: function (lat, lng) {
            var self = this;

            if (lat === this.lat && lng === this.lng) {
                return;
            }

            this.lat = lat;
            this.lng = lng;

            var geocoder = new google.maps.Geocoder;
            var latLng = new google.maps.LatLng(lat, lng);
            geocoder.geocode({'location': latLng}, function (results, status) {
                if (status === 'OK') {
                    if (self.$input) {
                        self.$input.val(results[0].formatted_address);
                        self._doAction();
                    }
                }
            });
        }
    });

    registry.add('place_autocomplete_multi', place_autocomplete_multi);
});
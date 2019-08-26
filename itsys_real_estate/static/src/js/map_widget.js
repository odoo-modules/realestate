/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('itsys_real_estate.map_widget', function (require) {
    var Widget = require('web.Widget');

    var MapWidget = Widget.extend({
        template: 'google_map',
        init: function (parent) {
            this.parent = parent || {};
            this._super(parent);
            // default location
            this.lat = parent.lat;
            this.lng = parent.lng;
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.on_ready();
            });
        },
        on_ready: function () {
            var self = this;

            if(!this.$el){
                return;
            }

            $(self.$el.filter('.map-toggle')[0]).click(function () {
                $(self.$el.filter('.gmap-container')[0]).toggle();
                self.update_marker(self.lat, self.lng);
            });

            // default latLng
            var latLng = new google.maps.LatLng(self.lat, self.lng);

            var mapOptions = {
                zoom: 12,
                center: latLng
            };

            this.map = new google.maps.Map(self.$el.filter('.gmap-container')[0], mapOptions);

            this.marker = new google.maps.Marker({
                position: latLng,
                map: self.map,
                draggable: true
            });
            // click event
            this.map.addListener('click', function (event) {
                var lat = event.latLng.lat();
                var lng = event.latLng.lng();
                // update marker
                var latLng = new google.maps.LatLng(lat, lng);
                self.marker.setPosition(latLng);
                google.maps.event.trigger(self.map, 'resize');
                // update place
                self.parent.update_place(lat, lng);
            });
            this.map.addListener('rightclick', function(event) {
                alert( 'Lat: ' + event.latLng.lat() + ' , Lng: ' + event.latLng.lng() );
            });
            // marker drag event
            this.marker.addListener('dragend', function (event) {
                var lat = event.latLng.lat();
                var lng = event.latLng.lng();
                self.parent.update_place(lat, lng);
            });

        },
        update_marker: function (lat, lng) {
            this.lat = lat;
            this.lng = lng;
            var latLng = new google.maps.LatLng(lat, lng);
            this.map.setCenter(latLng);
            this.marker.setPosition(latLng);
            google.maps.event.trigger(this.map, 'resize');
        }
    });

    return MapWidget;
});

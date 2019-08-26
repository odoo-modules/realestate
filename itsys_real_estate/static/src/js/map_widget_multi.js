/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('itsys_real_estate.map_widget_multi', function (require) {
    var Widget = require('web.Widget');

    var MapWidget = Widget.extend({
        template: 'google_map_multi',
        init: function (parent) {
            this.latlngList=parent.recordData.latlng_ids.data
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
                $(self.$el.filter('.gmap-container-multi')[0]).toggle();
                self.update_marker(self.lat, self.lng);
            });

            // default latLng
            var latLng = new google.maps.LatLng(self.lat, self.lng);

            var mapOptions = {
                zoom: 12,
                center: latLng
            };

            this.map = new google.maps.Map(self.$el.filter('.gmap-container-multi')[0], mapOptions);

            latlngList= this.latlngList
            for (var i=0;i<latlngList.length;i++){
                    if (latlngList[i]['data']['url']) {
                        icon_i= 'http://maps.google.com/mapfiles/ms/icons/'
                        if (latlngList[i]['data']['state']=='free') icon_i+='green-dot.png'
                        if (latlngList[i]['data']['state']=='reserved') icon_i+='blue-dot.png'
                        if (latlngList[i]['data']['state']=='sold') icon_i+='red-dot.png'
                        var url = latlngList[i]['data']['url']

                        var latLng = new google.maps.LatLng(latlngList[i]['data']['lat'], latlngList[i]['data']['lng']);
                        this.marker = new google.maps.Marker({
                            'url': latlngList[i]['data']['url'],
                            'map': self.map,
                            'position': latLng,
                            'draggable': false,
                            'animation': google.maps.Animation.DROP,
                            'icon': icon_i
                        });
                        google.maps.event.addListener(this.marker, 'click', function () {
                          window.location.href = this.url;
                        });
                }
            }

            this.map.addListener('click', function(event) {
                alert( 'Lat: ' + event.latLng.lat() + ' , Lng: ' + event.latLng.lng() );
            });
        },
        update_marker: function (lat, lng) {
            this.on_ready();
        }
    });

    return MapWidget;
});

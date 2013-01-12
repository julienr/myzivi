// Resize map canvas when resizing window
function windowResized() {
    var h = $(window).height();
    var offsetTop = $('#top_navbar').height(); // Calculate the top offset
    var mapheight = (h - offsetTop);
    $('#map_canvas').css('height', mapheight);
    // TODO: Need additional offset because of scrollbar. Not very clean
    $('#maplist').css('height', mapheight - 40);
}

// initialWorkspecs is a list of JSON workspecs
// N is the namespace to use for this app
function initMap(initialWorkspecs, N) {
    N.WorkSpec = Backbone.Model.extend({
        urlRoot: WORKSPEC_API,
    });

    N.WorkSpecList = Backbone.Collection.extend({
        urlRoot: WORKSPEC_API,
        model: N.WorkSpec,
    });

    // Backbone.Pageable doesn't work well with Backbone-tastypie
    // TODO: Write a client-side pagination lib

    N.WorkSpecView = Backbone.View.extend({
        tagName: "li",
        template: _.template($('#workspec_template').html()),
        initialize: function() {
            this.render();
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },
    });

    N.ListView = Backbone.View.extend({
        el: $("#maplist"),
        initialize: function() {
            this.collection.on('add', this.addOne, this);
            this.collection.on('reset', this.addAll, this);
            this.collection.on('all', this.render, this);
            //workspecs.fecth();
        },

        addOne: function(workspec) {
            var view = new N.WorkSpecView({model: workspec});
            this.$("#workspec-list").append(view.render().el);
        },

        addAll: function() {
            this.collection.each(this.addOne);
        },
    });

    N.MapView = Backbone.View.extend({
        el: $("#map_canvas"),
        infowindow_template : _.template($('#infowindow_template').html()),
        initialize: function() {
            _.bindAll(this, 'onViewChanged', 'onAdd', 'onRemove', 'onReset',
                      'onMarkerClick');

            var mapOptions = {
                center: new google.maps.LatLng(46.815099,8.22876),
                zoom: 8,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            this.map = new google.maps.Map(this.el, mapOptions);
            this.infowindow = new google.maps.InfoWindow();

            this.oms = new OverlappingMarkerSpiderfier(this.map);
            this.oms.addListener('click', this.onMarkerClick);

            var mcOptions = { maxZoom: 12 };
            this.markerCluster = new MarkerClusterer(this.map, [], mcOptions);

            $(window).resize(windowResized).resize();

            // -- Setup event listener

            // Register for the idle event (fired after movement).
            // This is the basis for interactivity and it will trigger a sync()
            // of the workspecs and map/list markers update
            // http://code.google.com/p/gmaps-api-issues/issues/detail?id=1371
            google.maps.event.addListener(this.map, 'idle', this.onViewChanged);

            this.collection.on('add', this.onAdd, this);
            this.collection.on('remove', this.onRemove, this);
            this.collection.on('reset', this.onReset, this);
        },

        onReset: function() {
            this.collection.each(this.onAdd);
        },

        // Called when a workspec is added to the collection
        onAdd: function(model) {
            var address = model.get("address");
            var lat = address.latitude;
            var lng = address.longitude;
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(lat, lng),
                map: this.map
            });
            marker.model = model;
            this.markerCluster.addMarker(marker);
            this.oms.addMarker(marker);
            model.marker = marker;
        },

        onRemove: function(model) {
            this.markerCluster.removeMarker(model.marker);
            this.oms.removeMarker(model.marker);
            model.marker.setMap(null);
            model.marker = null;
        },

        onMarkerClick: function(marker) {
            //this.infowindow.setContent(marker.desc);
            var html = this.infowindow_template(marker.model.toJSON());
            this.infowindow.setContent(html);
            this.infowindow.open(this.map, marker);
        },

        // Called when map view is changed by the user
        onViewChanged: function() {
            // Update collection by querying markers within new view bounds
            var bounds = this.map.getBounds();
            var swlat = bounds.getSouthWest().lat();
            var swlng = bounds.getSouthWest().lng();
            var nelat = bounds.getNorthEast().lat();
            var nelng = bounds.getNorthEast().lng();
            var params = {'latlngbb' : swlat.toString() + ","
                + swlng.toString() + "," + nelat.toString() + ","
                + nelng.toString()};
            // TODO: Re-enable, but need server-side clustering
            //console.log('onViewChanged => fetch')
            //this.collection.fetch({data: $.param(params), update:true});
        },
    });


    N.workspecs = new N.WorkSpecList([], {mode: 'client'});

    N.listview = new N.ListView({
      collection: N.workspecs
    });

    N.mapview = new N.MapView({
      collection: N.workspecs
    });

    // Boostrap initial data
    N.workspecs.reset(initialWorkspecs);

    // Populate with initial data
    //_.each(initialWorkspecs, function(jsonws){
        //var ws = new N.WorkSpec({
            //shortname: jsonws.fields.shortname,
            //url: jsonws.fields.url,
            //latlng: {'lat' : jsonws.fields.address.fields.latitude,
                     //'lng' : jsonws.fields.address.fields.longitude}
        //});
        //N.workspecs.add(ws);
    //});

}

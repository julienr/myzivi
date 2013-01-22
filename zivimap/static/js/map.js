// Resize map canvas when resizing window
function windowResized() {
    var h = $(window).height();
    var offsetTop = $('#top_navbar').height(); // Calculate the top offset
    var mapheight = (h - offsetTop);
    $('#map_canvas').css('height', mapheight);
    // TODO: Need additional offset because of scrollbar. Not very clean
    $('#maplist').css('height', mapheight - 40);
}


var ZIVI_WS_BASE = 'http://www.eis.zivi.admin.ch/ZiviEis/WorkSpecificationDetail.aspx?prevFunctionId=123F61E5-F417-4F51-AC59-906D6F999D02';
function url_from_phid(phid) {
    return ZIVI_WS_BASE + '&phid=' + phid;
}

// initialWorkspecs is a list of JSON workspecs
// N is the namespace to use for this app
function initMap(initialWorkspecs, initialAddresses, N) {
    N.WorkSpec = Backbone.Model.extend({
        urlRoot: SEARCH_API,
    });

    N.Address = Backbone.Model.extend({
        urlRoot: ADDRESS_API,
        // We don't use resource_uri for addresses
        idAttribute: 'id',
    });

    N.WorkSpecList = Backbone.Collection.extend({
        urlRoot: SEARCH_API,
        model: N.WorkSpec,
    });

    N.AddressList = Backbone.Collection.extend({
        urlRoot: ADDRESS_API,
        model: N.Address
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
        addresses: null,

        initialize: function(options) {
            if (options.addresses) {
                this.addresses = options.addresses;
            }

            _.bindAll(this, 'onViewChanged', 'onAdd', 'onRemove', 'onReset',
                      'onMarkerClick', 'zoomToCluster', 'displayClusterInfo');

            var mapOptions = {
                center: new google.maps.LatLng(46.815099,8.22876),
                zoom: 8,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            this.map = new google.maps.Map(this.el, mapOptions);
            this.infowindow = new google.maps.InfoWindow();

            // We handle click events and maxZoom ourselves
            // - maxZoom is used to specify the maximum level at which to
            //   create clusters
            // - maxViewZoom is the max level at which we'll zoom when a
            //   user clicks on a cluster
            // We set maxZoom to null because we always want clusters. But
            // we set a reasonable maximum zoom level of 12 considering that
            // we mostly have city-level localization, going to road-level
            // is pretty meaningless
            var mcOptions = { maxZoom: null, zoomOnClick: false, minimumClusterSize: 1 };
            this.markerCluster = new MarkerClusterer(this.map, [], mcOptions);
            this.markerCluster.maxViewZoom = 12;

            $(window).resize(windowResized).resize();

            // -- Setup event listener
            var mapview = this;
            google.maps.event.addListener(this.markerCluster, 'click', function(cluster) {
                if (mapview.map.getZoom() >= mapview.markerCluster.maxViewZoom) {
                    // If we're already at max zoom, show a popup with the
                    // list of workspecs in the cluster
                    console.log('Max zoom');
                    mapview.displayClusterInfo(cluster);
                } else {
                    mapview.zoomToCluster(cluster);
                }
            });

            // Register for the idle event (fired after movement).
            // This is the basis for interactivity and it will trigger a sync()
            // of the workspecs and map/list markers update
            // http://code.google.com/p/gmaps-api-issues/issues/detail?id=1371
            google.maps.event.addListener(this.map, 'idle', this.onViewChanged);

            this.collection.on('add', this.onAdd, this);
            this.collection.on('remove', this.onRemove, this);
            this.collection.on('reset', this.onReset, this);
        },

        // Called to display the workspecs contained in the cluster in the
        // infowindow
        displayClusterInfo: function(cluster) {
            var markers = cluster.getMarkers();
            var lst = _.map(markers, function(m) {
                return '<li>' + this.infowindow_template(m.model.toJSON()) + '</li>';
            }, this);
            var html = _.reduceRight(lst, function(a, b) {
                return a.concat(b);
            }, "");
            this.infowindow.setContent('<ul>' + html + '</ul>');
            this.infowindow.open(this.map);
            this.infowindow.setPosition(cluster.getCenter());
        },

        zoomToCluster: function(cluster) {
            // Modified copy of default zoom function from markerClustererPlus
            // Zoom into the cluster.
            //mz = this.markerCluster.getMaxZoom();
            mz = this.markerCluster.maxViewZoom;
            theBounds = cluster.getBounds();
            this.map.fitBounds(theBounds);
            // There is a fix for Issue 170 here:
            var map = this.map;
            setTimeout(function () {
                map.fitBounds(theBounds);
                // Don't zoom beyond the max zoom level
                // Because fitBounds will zoom, this check we didn't zoom too
                // far
                if (mz !== null && (map.getZoom() > mz)) {
                    map.setZoom(mz + 1);
                }
            }, 100);
        },

        onReset: function() {
            this.collection.each(this.onAdd);
        },

        // Called when a workspec is added to the collection
        onAdd: function(model, options) {
            var addrid = model.get("addrid");
            var address = this.addresses.get(addrid);
            var lat = address.get("latitude");
            var lng = address.get("longitude");
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(lat, lng),
                map: this.map
            });
            marker.model = model;
            this.markerCluster.addMarker(marker);
            model.marker = marker;
        },

        onRemove: function(model) {
            this.markerCluster.removeMarker(model.marker);
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
            //console.log('onViewChanged => fetch')
            //this.collection.fetch({data: $.param(params), update:true});
        },
    });

    N.addresses = new N.AddressList(initialAddresses);
    N.workspecs = new N.WorkSpecList();

    //N.listview = new N.ListView({
        //collection: N.workspecs
    //});

    N.mapview = new N.MapView({
        collection: N.workspecs,
        addresses: N.addresses,
    });

    N.workspecs.reset(initialWorkspecs);
}

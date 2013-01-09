// Resize map canvas when resizing window
function windowResized() {
    var h = $(window).height();
    var offsetTop = 0; // Calculate the top offset
    $('#map_canvas').css('height', (h - offsetTop));
}

// initialWorkspecs is a list of JSON workspecs
// N is the namespace to use for this app
function initMap(initialWorkspecs, N) {
    N.WorkSpec = Backbone.Model.extend({});

    N.WorkSpecList = Backbone.Collection.extend({
        model: N.WorkSpec,
    });

    N.workspecs = new N.WorkSpecList;

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
            this.collection.bind('add', this.addOne, this);
            this.collection.bind('reset', this.addAll, this);
            this.collection.bind('all', this.render, this);
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
      initialize: function() {
        var mapOptions = {
          center: new google.maps.LatLng(46.815099,8.22876),
          zoom: 8,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map_canvas"),
                                      mapOptions);
        var infowindow = new google.maps.InfoWindow();

        var oms = new OverlappingMarkerSpiderfier(map);
        oms.addListener('click', function(marker) {
            infowindow.setContent(marker.desc);
            infowindow.open(map, marker);
        });

        var mcOptions = { maxZoom: 12 };
        var markerCluster = new MarkerClusterer(map, [], mcOptions);

        $(window).resize(windowResized).resize();

        // Bind event to collection
        this.collection.bind('add', function(model) {
          var mpos = model.get("latlng");
          marker = new google.maps.Marker({
            position: new google.maps.LatLng(mpos.lat, mpos.lng),
            map:map
          });
          marker.desc = model.get("url");
          markerCluster.addMarker(marker);
          oms.addMarker(marker);
        });
      },
    });

    N.list = new N.ListView({
      collection: N.workspecs
    });
    N.map = new N.MapView({
      collection: N.workspecs
    });

    // Populate with initial data
    _.each(initialWorkspecs, function(jsonws){
        var ws = new N.WorkSpec({
            shortname: jsonws.fields.shortname,
            url: jsonws.fields.url,
            latlng: {'lat' : jsonws.fields.address.fields.latitude,
                     'lng' : jsonws.fields.address.fields.longitude}
        });
        N.workspecs.add(ws);
    });

}

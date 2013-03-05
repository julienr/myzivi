// Resize map canvas when resizing window
function windowResized() {
    var h = $(window).height();
    var offsetTop = $('#top_navbar').height(); // Calculate the top offset
    var mapheight = (h - offsetTop);
    $('#map_canvas').css('height', mapheight);
    // TODO: Need additional offset because of scrollbar. Not very clean
    //$('#maplist').css('height', mapheight - 40);
}


var ZIVI_WS_BASE = 'http://www.eis.zivi.admin.ch/ZiviEis/WorkSpecificationDetail.aspx?prevFunctionId=123F61E5-F417-4F51-AC59-906D6F999D02';
function url_from_phid(phid) {
    return ZIVI_WS_BASE + '&phid=' + phid;
}


// MapView prototype
MapView = function() {
  this.initialize.apply(this, arguments);
}

MapView.prototype.initialize = function(el, infowindow_template) {
  this.infowindow_template = infowindow_template;
  _.bindAll(this, 'onViewChanged', 'onMarkerClick', 'zoomToCluster', 'displayClusterInfo');

  var mapOptions = {
      center: new google.maps.LatLng(46.815099,8.22876),
      zoom: 8,
      mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  this.map = new google.maps.Map(el, mapOptions);
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
}

// Called to display the workspecs contained in the cluster in the
// infowindow
MapView.prototype.displayClusterInfo = function(cluster) {
  var markers = cluster.getMarkers();
  var lst = _.map(markers, function(m) {
      return '<li>' + this.infowindow_template(m.workspec) + '</li>';
  }, this);
  var html = _.reduceRight(lst, function(a, b) {
      return a.concat(b);
  }, "");
  this.infowindow.setContent('<ul>' + html + '</ul>');
  this.infowindow.open(this.map);
  this.infowindow.setPosition(cluster.getCenter());
}

MapView.prototype.zoomToCluster = function(cluster) {
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
}

MapView.prototype.onMarkerClick = function(marker) {
  //this.infowindow.setContent(marker.desc);
  var html = this.infowindow_template(marker.model.toJSON());
  this.infowindow.setContent(html);
  this.infowindow.open(this.map, marker);
}

MapView.prototype.setAddresses = function(addresses) {
  this.addresses = addresses;
}

MapView.prototype.createMarkersFromWorkSpecs = function(workspecs) {
  var markers = new Array();
  var length = workspecs.length;
  for (var i = 0; i < length; i++) {
    var ws = workspecs[i];
    var addrid = ws.addrid;
    var address = this.addresses[addrid];
    var lat = address.latitude;
    var lng = address.longitude;
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(lat, lng),
        map: this.map
    });
    marker.workspec = ws;
    ws.marker = marker;
    markers.push(marker);
  }
  this.markerCluster.addMarkers(markers);
}

// Called when map view is changed by the user
MapView.prototype.onViewChanged = function() {
  // Update collection by querying markers within new view bounds
  //var bounds = this.map.getBounds();
  //var swlat = bounds.getSouthWest().lat();
  //var swlng = bounds.getSouthWest().lng();
  //var nelat = bounds.getNorthEast().lat();
  //var nelng = bounds.getNorthEast().lng();
  //var params = {'latlngbb' : swlat.toString() + ","
      //+ swlng.toString() + "," + nelat.toString() + ","
      //+ nelng.toString()};
  //console.log('onViewChanged => fetch')
  //this.collection.fetch({data: $.param(params), update:true});

}



function newInitMap(N) {
  // Called on ajax errors
  N.onAjaxFail = function() {
    alert('Oops, something went wrong. Try reloading');
  }

  // Called when addresses are received from API
  N.onAddresses = function(response) {
    N.addresses = {}
    var objs = response.objects;
    var length = objs.length;
    for (var i = 0; i < length; i++) {
      N.addresses[objs[i].id] = objs[i];
    }
    N.mapView.setAddresses(N.addresses);
  };

  N.onWorkSpecs = function(response) {
    N.mapView.createMarkersFromWorkSpecs(response.objects);
  };

  N.mapView = new MapView($("#map_canvas")[0],
                          _.template($('#infowindow_template').html()));


  // Chain address loading and then workspecs loading
  $('#loading').show();
  $.getJSON(ADDRESS_API)
    .done(function(response) {
      N.onAddresses(response);
      $.getJSON(SEARCH_API)
        .done(function(response) {
          N.onWorkSpecs(response);
          $('#loading').hide();
        })
        .fail(N.onAjaxFailed);
    })
    .fail(N.onAjaxFail)
}

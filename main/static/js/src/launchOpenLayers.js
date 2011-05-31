var defaultLayers = [
    ["Nigeria", "nigeria_base"],
    ["Nigeria health workers per thousand people", "nigeria_healthworkers_per_thousand"],
    ["Nigeria Health Facilities with Institutional Deliveries", "pct_healthfacilities_with_institutional_delivery"],
    ["Nigeria No Stockouts of Bednets or Malaria Medicine", "nigeria_pct_no_bednet_malmeds_oneweek"],
    ["Nigeria Classrooms That Need Repair", "nigeria_pct_classroom_need_repair"],
    ["Nigeria classrooms with proportion student to teacher ratio > 40", "nigeria_prop_ratio_greater_than_40"],
    ["Nigeria Immunization Rate", "nigearia_immunization_rate"],
    ["Nigeria Under 5 Mortality Rate", "nigeria_under5_mortality_rate"],
    ["Nigeria Child Wasting", "nigeria_wasting"],
    ["Nigeria Child Health", "nigeria_child_health"],
    ["Nigeria Child Nutrition", "nigeria_child_nutrition"],
    ["Nigeria Maternal Health", "nigeria_maternal_health"],
    ["Nigeria Primary Education Enrollment", "nigeria_primary_education_enrollment"]
  ];

var LaunchOpenLayers = (function (wrapId, _opts) { 
  var wrap = $('#'+wrapId);
  var defaultOpts = {
      centroid: {          
          lat: 0.000068698255561324,
          lng: 0.000083908685869343
      },
      points: false,
      latLngs: false,
      boundingBox: false,
      mapHeight: 475,
      localTiles: false,
      layerSelector: '#layer-select',
      tileUrl: "http://tilestream.openmangrove.org:8888/",
      tileCache: "http://localhost:8000/tiles/",
      layers: defaultLayers,
      zoom: 6
  }, opts = $.extend({}, defaultOpts, _opts);

  wrap.css({'height':opts.mapHeight});
  OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
  OpenLayers.ImgPath = "http://js.mapbox.com/theme/dark/";
  var options = {
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
//    numZoomLevels: 9,
    maxResolution: 156543.0339,
    restrictedExtent: new OpenLayers.Bounds(
        -4783.9396188051, 463514.13943762, 1707405.4936624, 1625356.9691642
    ),
    maxExtent: new OpenLayers.Bounds(
	-20037500,
	-20037500,
      20037500,
      20037500
    ) 
  };
  
  map = new OpenLayers.Map(wrapId, options);
  var mapserver = !!opts.localTiles ? 
                    opts.tileCache : opts.tileUrl;
                    
  var mapLayers = $.map(opts.layers, function(i, ldata){
      return new OpenLayers.Layer.TMS(ldata[0], [mapserver], 
          {
              layername: ldata[1],
              'type': 'png'
          });
  });
  mapLayers.push(new OpenLayers.Layer.Google(
      "Google Satellite",
      {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
      ));
  mapLayers.push(new OpenLayers.Layer.Google(
      "Google Physical",
      {type: google.maps.MapTypeId.TERRAIN}
      ));
  
  map.addLayers(mapLayers);
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.setCenter(new OpenLayers.LonLat(opts.centroid.lng, opts.centroid.lat), opts.zoom)

  if(!!opts.layerSelector) {
      $(opts.layerSelector).change(function(param){
          layer_id = $(this).val();
          layer = eval(layer_id);
          layer.map.setBaseLayer(layer);
          $('.mapped-indicator').hide();
          $('#mapped-'+layer_id).show();
      })
  }
  if(!!opts.points) {
      var markers = new OpenLayers.Layer.Markers("Markers");
      map.addLayer(markers);
      var icon = (function(pointData){
          var iconType = "health"; // for example
          if(icons[iconType]===undefined) {
                var iconUrl = 'http://www.openlayers.org/dev/img/marker.png';
                var size = new OpenLayers.Size(21,25);
                var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
                icons[iconType] = new OpenLayers.Icon(iconUrl), size, offset);
            }
            return icons[iconType];
        });
        
        var bounds = new OpenLayers.Bounds();
    	$.each(opts.points, function(i, d){
    		var _ll = d.latlng.split(",");
    		var ll = [+_ll[0], +_ll[1]];
            bounds.extend(new OpenLayers.LonLat(ll[1], ll[0]));
            markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(ll[1], ll[0]), icon(d)));
    	});
        map.zoomToExtent(bounds);
    }
});

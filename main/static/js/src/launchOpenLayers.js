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
      tileUrl: "http://tilestream.openmangrove.org:8888/",
      tileCache: "http://localhost:8000/tiles/",
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
  var nigeria = new OpenLayers.Layer.TMS(
    "Nigeria",
    [ mapserver],
    { 'layername': 'nigeria_base', 'type': 'png' }
  );

    

  var nigeria_healthworkers_per_thousand  = new OpenLayers.Layer.TMS(
    "Nigeria health workers per thousand people",
    [mapserver],
    {'layername': 'nigeria_healthworkers_per_thousand', 'type': 'png'}
  );

  var pct_healthfacilities_with_institutional_delivery  = new OpenLayers.Layer.TMS(
    "Nigeria Health Facilities with Institutional Deliveries",
    [mapserver],
    {'layername': 'pct_healthfacilities_with_institutional_delivery', 'type': 'png'}
  );

  var nigeria_pct_no_bednet_malmeds_oneweek  = new OpenLayers.Layer.TMS(
    "Nigeria No Stockouts of Bednets or Malaria Medicine",
    [mapserver],
    {'layername': 'nigeria_pct_no_bednet_malmeds_oneweek', 'type': 'png'}
  );

  var nigeria_pct_classroom_need_repair  = new OpenLayers.Layer.TMS(
    "Nigeria Classrooms That Need Repair",
    [mapserver],
    {'layername': 'nigeria_pct_classroom_need_repair', 'type': 'png'}
  );

  var nigeria_prop_ratio_greater_than_40  = new OpenLayers.Layer.TMS(
    "Nigeria classrooms with proportion student to teacher ratio > 40",
    [mapserver],
    {'layername': 'nigeria_prop_ratio_greater_than_40', 'type': 'png'}
  );


  var nigearia_immunization_rate = new OpenLayers.Layer.TMS(
    "Nigeria Immunization Rate",
    [mapserver],
    {'layername': 'nigearia_immunization_rate', 'type': 'png'}
  );

  var nigeria_under5_mortality_rate = new OpenLayers.Layer.TMS(
    "Nigeria Under 5 Mortality Rate",
    [ mapserver],
    { 'layername': 'nigeria_under5_mortality_rate', 'type': 'png' }
  );

  var nigeria_wasting = new OpenLayers.Layer.TMS(
    "Nigeria Child Wasting",
    [ mapserver],
    { 'layername': 'nigeria_wasting', 'type': 'png' }
  );

  var nigeria_child_health = new OpenLayers.Layer.TMS(
    "Nigeria Child Health",
    [mapserver],
    {'layername': 'nigeria_child_health', 'type': 'png'}
  );
  var nigeria_child_nutrition = new OpenLayers.Layer.TMS(
    "Nigeria Child Nutrition",
    [mapserver],
    {'layername': 'nigeria_child_nutrition', 'type': 'png'}
  );

  var nigeria_malaria = new OpenLayers.Layer.TMS(
    "Nigeria Malaria",
    [mapserver],
    {'layername': 'nigeria_malaria', 'type': 'png'}
  );

  var nigeria_maternal_health = new OpenLayers.Layer.TMS(
    "Nigeria Maternal Health",
    [mapserver],
    {'layername': 'nigeria_maternal_health', 'type': 'png'}
  );


  var nigeria_primary_education_enrollment = new OpenLayers.Layer.TMS(
    "Nigeria Primary Education Enrollment",
    [mapserver],
    {'layername': 'nigeria_primary_education_enrollment', 'type': 'png'}
  );

 var gsat = new OpenLayers.Layer.Google(
    "Google Satellite",
    {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
  );

  var gphy = new OpenLayers.Layer.Google(
        "Google Physical",
    {type: google.maps.MapTypeId.TERRAIN}
  );

    map.addLayers([nigeria, nigeria_healthworkers_per_thousand, pct_healthfacilities_with_institutional_delivery, nigeria_pct_no_bednet_malmeds_oneweek, nigeria_pct_classroom_need_repair, nigeria_prop_ratio_greater_than_40, nigearia_immunization_rate, nigeria_child_health, nigeria_child_nutrition, nigeria_malaria, nigeria_maternal_health, nigeria_wasting, nigeria_under5_mortality_rate, nigeria_primary_education_enrollment, gsat, gphy]);

  map.addControl(new OpenLayers.Control.LayerSwitcher());

  var center = new OpenLayers.LonLat(opts.centroid.lng, opts.centroid.lat);
  map.setCenter(center, opts.zoom)

    $('#layer-select').change(function(param) {

        layer_id = $(this).val();
        layer = eval(layer_id);

        layer.map.setBaseLayer(layer);

        $('.mapped-indicator').hide();
        $('#mapped-'+layer_id).show();
    });  

    if(!!opts.points) {
        var markers = new OpenLayers.Layer.Markers( "Markers" );
        map.addLayer(markers);
        
        var icon = (function(){
            var size = new OpenLayers.Size(21,25);
            var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            return new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
        })();
        
        var bounds = new OpenLayers.Bounds();
        var lls = [];
    	$.each(opts.points, function(i, d){
    		var _ll = d.latlng.split(",");
    		var ll = [+_ll[0], +_ll[1]];
            bounds.extend(new OpenLayers.LonLat(ll[1], ll[0]));
            markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(ll[1], ll[0]), icon));
    	});
    	
        map.zoomToExtent(bounds);
    }
})



var LaunchOpenLayers = (function (_wrap) { 
  $("#map").height(475);

  OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
  OpenLayers.ImgPath = "http://js.mapbox.com/theme/dark/";
  var options = {
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
    numZoomLevels: 11,
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
  
  map = new OpenLayers.Map('map', options);
  var mapserver = "http://tilestream.openmangrove.org:8888/";
  
  var nigeria = new OpenLayers.Layer.TMS(
    "Nigeria",
    [ mapserver],
    { 'layername': 'nigeria_base', 'type': 'png' }
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

 var gsat = new OpenLayers.Layer.Google(
    "Google Satellite",
    {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
  );

  var gphy = new OpenLayers.Layer.Google(
        "Google Physical",
    {type: google.maps.MapTypeId.TERRAIN}
  );

  map.addLayers([nigeria, nigeria_child_health, nigeria_child_nutrition, nigeria_malaria, nigeria_maternal_health, gphy, gsat]);

  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.setCenter(new OpenLayers.LonLat(851310.77702182, 1044435.5543009), 6);
  

})

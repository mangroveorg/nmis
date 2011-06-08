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
      centroidGoogleLatLng: false,
      points: false,
      latLngs: false,
      boundingBox: false,
      mapHeight: 475,
      transparentIconOpacity: 0,
      localTiles: false,
      layerSelector: '#layer-select',
      tileUrl: "http://tilestream.openmangrove.org:8888/",
      tileCache: "http://localhost:8000/tiles/",
      layers: defaultLayers,
      zoom: 6
  }
  var opts = $.extend({}, defaultOpts, _opts);

  if(opts.centroidGoogleLatLng !== false) {
      function convertDamnCentroid(fromCoord) {
                // convert standard lat long measurements to google projection
                //convert from EPSG:900913 to EPSG:4326
                var point = new OpenLayers.LonLat(fromCoord.lng, fromCoord.lat);
                return point.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
        }
      opts.centroid = convertDamnCentroid(opts.centroidGoogleLatLng);
  }
  wrap.css({'height':opts.mapHeight});
  OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
  
  OpenLayers.ImgPath = "/static/openlayers/default/img/";
  var options = {
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
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
                
  var mapLayers = $.map(opts.layers, function(ldata, i){
      return new OpenLayers.Layer.TMS(ldata[0], [mapserver], 
          {
              layername: ldata[1],
              'type': 'png'
          });
  });
  if(typeof(google)!=='undefined') {
        mapLayers.push(new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
            ));
        mapLayers.push(new OpenLayers.Layer.Google(
            "Google Physical",
            {type: google.maps.MapTypeId.TERRAIN}
            ));
  }
  map.addLayers(mapLayers);
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  if(opts.centroid instanceof OpenLayers.LonLat) {
      map.setCenter(opts.centroid, opts.zoom);
  } else {
      map.setCenter(new OpenLayers.LonLat(opts.centroid.lng, opts.centroid.lat), opts.zoom);
  }

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
      //this stuff _should_ be moved to a separate area of the code...
      var markers = new OpenLayers.Layer.Markers("Markers");
        var iconMakers = {};
        var flagColors = "blue green orange pink purple red yellow".split(" ");
  		var stColors = {
  			water: "blue",
  			health: "red",
  			agriculture: "orange",
  			lga: "purple",
  			education: "green",
  			defaultColor: "pink"
  		};
  		$.each(stColors, function(k, val){
  		    iconMakers[k] = function(){
  		        var url = "/static/images/geosilk/flag_"+val+".png";
      		    var size = new OpenLayers.Size(16,16);
      		    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
  		        return new OpenLayers.Icon(url, size, offset);
  		    }
  		});
      map.addLayer(markers);
        var bounds = new OpenLayers.Bounds();
    	$.each(opts.points, function(i, d){
    	        if(d.latlng!==undefined) {
    	            var iconSector = (d.sector || 'default').toLowerCase();
            	    var icon = (iconMakers[iconSector] || iconMakers.defaultColor)();
            	    var ll = d.latlng;
            	    var oLl = new OpenLayers.LonLat(ll[1], ll[0]).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));;
            	    d.mrkr = new OpenLayers.Marker(oLl, icon);
            	    d.mrkr.facilityUid = d.uid;
            	    d.mrkr.events.on({
            	        'click': function(evt){
            	            $(evt.element).trigger('facility-click', {'uid': d.uid});
            	        }
            	    });
            	    markers.addMarker(d.mrkr);
            	    bounds.extend(oLl);
    	        } 
    	});
    	var markerCount = 0;
        map.zoomToExtent(bounds);
        window.filterPointsBySector = function(sector){
            if(sector==='all') {
                console.log("show all sectors");
            } else {
                $.each(opts.points, function(i, pt){
                    if(pt.sector === sector) {
                        //make opaque
                        $(pt.mrkr.icon.imageDiv).show();
                    } else {
                        //make semi-transparent and low z-index
                        $(pt.mrkr.icon.imageDiv).hide();
                    }
                });
            }
        }
        showingSector !== undefined && filterPointsBySector(showingSector);
    }
});

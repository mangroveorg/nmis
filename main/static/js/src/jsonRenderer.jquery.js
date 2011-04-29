(function($, undefined){
	var j$ = {};
	j$.mdg_data = function(data){
	    if($.createMdgTable!==undefined) {
	        return $('<div />').html($.createMdgTable(data.mdg_data))
	    }
	}
	j$.html = function(data){
		return $("<div />").html(data.html);
	}
	j$.test_json_renderer = function(data){
		return $("<div />").text(JSON.stringify(data));
	}
	j$.notFound = function(data){
		return $('<p />').text('Widget renderer not found -- '+data.display_method);
	}
	$.renderJsonWidget = function(c){
	    var r = j$[c.display_method];
	    if(r!==undefined) {return r(c)}
	    return j$.notFound(c);
	}
	$.renderJsonWidgetToElem = function(elem){
	    return function(i, c){$(elem).append($.renderJsonWidget(c).addClass('widget'))}
	}
	$.jsonRenderers = j$;
})(jQuery);

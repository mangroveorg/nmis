var LaunchRoysMap = (function(_wrap) {
    var wrap = $(_wrap);
    tags = [];

    // Prepare page
    $('a', wrap).hover(
        function () {this.className = this.className.replace('OFF', 'ON');}, 
        function () {this.className = this.className.replace('ON', 'OFF');}
    );
    function getNumber(x) {return /\d+/.exec(x)[0]}
    function getID(obj) {return getNumber(obj.id)}
    function compareByName(a, b) {
        var nameA = a.name.toLowerCase(), nameB = b.name.toLowerCase();
        if (nameA < nameB) return -1;
        else if (nameA > nameB) return 1;
        else return 0;
    }

    // Define functions
    function refreshInterface() {
        loadTags();
        renderMaps();
    }
    function loadTags() {
        $.get('/xss/tags.json', {
            key: $('#key', wrap).val()
        }, function(data) {
            var targetDiv = $('#tags', wrap);
            $(data.split('\n')).each(function() {
                var tag = $.trim(this);
                if (!tag) return;
                targetDiv.append('<input type=checkbox class=tag value="' + tag + '">' + tag + '<br>');
            });
            $('.tag', wrap).change(renderMaps);
        });
    }
    function getSelectedTags() {
        
        $('.tag:checked', wrap).each(function() {
            tags.push(this.value);
        });
        return tags.join('\n');
    }
    
    var propertyByNameByID = {}, elementsByID = {}, geometriesByID = {};
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        // Clean
        if (layer) map.remove(layer);
        if (!tagString) return;
        layer = po.geoJson().url('/xss/maps.json?key=' + window.csrf + '&srid=4326&tags=' + escape(tagString) + "&bboxFormat=xyxy&bbox={B}&simplified=1").id('features').on('load', function(e) {
            // For each feature,
            $(e.features).each(function() {
                // Load
                var featureID = this.data.id;
                // Store propertyByName
                propertyByNameByID[featureID] = this.data.properties;
                // Store element
                if (!elementsByID[featureID]) elementsByID[featureID] = []
                elementsByID[featureID].push(this.element);
                // Store geometry
                if (!geometriesByID[featureID]) geometriesByID[featureID] = []
                geometriesByID[featureID].push(this.data.geometry);
                // Set hover listener
                this.element.addEventListener('mouseover', getHoverFeature(featureID), false);
                this.element.addEventListener('mouseout', getUnhoverFeature(featureID), false);
                // Set click listener
                this.element.addEventListener('click', getSelectFeature(featureID), false);
                // Set color class
                this.element.setAttribute('class', getColorClass(featureID));
                // Set id
                this.element.setAttribute('id', 'e' + featureID);
            });
            // Initialize
            var items = [];
            // For each stored feature,
            for (featureID in propertyByNameByID) {
                // If the feature is visible,
                if ($('#e' + featureID, wrap).length) {
                    propertyByName = propertyByNameByID[featureID];
                    items.push({
                        featureID: featureID,
                        name: propertyByName['Name'] || featureID + ''
                    });
                } 
                // If the feature is not visible,
                else {
                    delete propertyByNameByID[featureID];
                }
            }
            // Sort
            items.sort(compareByName);
            // Display
            var listLines = [];
            $(items).each(function() {
                listLines.push('<div class="fN feature" id=d' + this.featureID + '>' + this.name + '</div>');
            });
            $('#list', wrap).html(listLines.join('\n'));
            $('#list .feature', wrap).hover(
                function () {
                    scrollList = 0;
                    getHoverFeature(getID(this))();
                    scrollList = 1;
                }, 
                function () {
                    scrollList = 0;
                    getUnhoverFeature(getID(this))();
                    scrollList = 1;
                }
            ).click(function() {
                getSelectFeature(getID(this))();
            });
        });
        map.add(layer);
    }

    // Define factories
    var scrollList = 1;
    function getHoverFeature(featureID) {
        return function(e) {
            // Highlight list entry
            var listHover = $('#d' + featureID, wrap);
            if (listHover) {
                listHover.removeClass('bN bS').addClass('bH');
                if (scrollList) {
                    // Scroll list
                    var list = $('#list', wrap);
                    list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
                }
            }
            // Highlight map entry
            setFeatureColor(featureID, 'fH');
        };
    }
    function getUnhoverFeature(featureID) {
        return function(e) {
            // Restore list entry
            var listHover = $('#d' + featureID, wrap);
            listHover.removeClass('bH bS').addClass('bN');
            // Restore map entry
            setFeatureColor(featureID, getColorClass(featureID));
        }
    }
    function getSelectFeature(featureID) {
        return function(e) {
            if (selectedID && selectedID != featureID) {
                // Restore list entry
                var listSelect = $('#d' + selectedID, wrap);
                if (listSelect) listSelect.removeClass('bH bS').addClass('bN');
                // Restore map entry
                setFeatureColor(selectedID, getColorClass(selectedID));
            }
            // Load
            selectedID = featureID;
            // Highlight list entry
            var listSelect = $('#d' + selectedID, wrap);
            listSelect.removeClass('bN bH').addClass('bS');
            // Highlight map entry
            setFeatureColor(selectedID, 'fS');
            // Set feature detail
            var propertyByName = propertyByNameByID[selectedID], propertyLines = [];
            for (key in propertyByName) {
                propertyLines.push(key + ' = ' + propertyByName[key]);
            }
            propertyLines.sort();
            $('#detail', wrap).html('<div id=detailHeader>' + propertyByName['Name'] + '</div><br>' + propertyLines.join('<br>'));
        };
    }
    function getColorClass(featureID) {
        return 'q' + (8 - (featureID % 9)) + '-' + 9;
    }
    function setFeatureColor(featureID, colorClass) {
        $(elementsByID[featureID], wrap).each(function() {
            this.setAttribute('class', colorClass);
        });
    }

    // Make map using Polymaps
    var po = org.polymaps;
    map = po.map()
        .container(document.getElementById('map').appendChild(po.svg('svg')))
        .center({lat: 40.7143528, lon: -74.0059731})
        .zoom(0)
        .add(po.interact())
        .add(po.image().url(po.url('http://mt{S}.googleapis.com/vt?src=apiv3&x={X}&y={Y}&z={Z}').hosts(['0', '1', '2', '3', ''])))
        .add(po.compass().pan('none'));
    map.container().setAttribute('class', 'Blues');
    var selectedID;
    $('#detail', wrap).hover(
        function() {
            if (selectedID) {
                $(this).css('background-color', '#b2b2b2');
            }
        },
        function() {
            $(this).css('background-color', '#cccccc');
        }
    ).click(function() {
        if (selectedID) {
            // Initialize
            var mapExtent = map.extent(), mapLL = mapExtent[0], mapUR = mapExtent[1];
            var minLon = mapUR.lon, minLat = mapUR.lat, maxLon = mapLL.lon, maxLat = mapLL.lat;
            var geometries = geometriesByID[selectedID];
            var queue = [];
            for (var i = 0; i < geometries.length; i++) {
                queue.push(geometries[i].coordinates);
            }
            while (queue.length) {
                var object = queue.pop();
                if (typeof object[0] == 'number') {
                    var lon = object[0], lat = object[1];
                    if (lon < minLon) minLon = lon;
                    if (lon > maxLon) maxLon = lon;
                    if (lat < minLat) minLat = lat;
                    if (lat > maxLat) maxLat = lat;
                } else {
                    for (var i = 0; i < object.length; i++) {
                        queue.push(object[i]);
                    }
                }
            }
            // Scale to include more background
            var scalingFactor = 1.2;
            var xLengthHalved = (maxLon - minLon) / 2;
            var yLengthHalved = (maxLat - minLat) / 2;
            // Zoom to scaled feature extent
            map.extent([{
                lon: minLon + (1 - scalingFactor) * xLengthHalved,
                lat: minLat + (1 - scalingFactor) * yLengthHalved
            }, {
                lon: minLon + (1 + scalingFactor) * xLengthHalved,
                lat: minLat + (1 + scalingFactor) * yLengthHalved
            }]);
        }
    });


    // Prepare page
    refreshInterface();
    $('#refresh', wrap).click(refreshInterface);
    $('#key', wrap).click(function() {this.select()}).focus();
});

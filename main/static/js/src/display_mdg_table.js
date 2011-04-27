
(function($){
	function CreateMDGTable(data) {
		var years = data.years;
		var variables = data.variables;
		var goalNums = [];
		var goals = {};
		var goalText = [
		    "Goal 1 &raquo; Eradicate extreme poverty and hunger",
		    "Goal 2 &raquo; Achieve universal primary education",
		    "Goal 3 &raquo; Promote gender equality and empower women",
		    "Goal 4 &raquo; Reduce child mortality rates",
		    "Goal 5 &raquo; Improve maternal health",
		    "Goal 6 &raquo; Combat HIV/AIDS, malaria, and other diseases",
		    "Goal 7 &raquo; Ensure environmental sustainability",
		    "Goal 8 &raquo; Develop a global partnership for development"
		];
		function createRowForVariable(goalData) {
			var tr = $("<tr />");
			if(goalData.subgoal==undefined) {
				tr.append($("<td />", {'class':'subgoal empty'}))
			} else {
				tr.append($("<td />", {'class':'subgoal'}).text(goalData.subgoal))
			}
			var goalName = $("<td />").text(goalData.name);
			tr.append(goalName)
			
			if(goalData.subgroup==undefined) {
				goalName.attr('colspan', 2)
			} else {
				tr.append($("<td />").text(goalData.subgroup))
			}
			
			$.each(years, function(iy, year){
				var yv = goalData.values[''+year]
				tr.append($("<td />").text(yv))
			})
			
			return tr;
		}
		
		var goalNumStrs = []
		$.each(variables, function(pk, variable){
			if(goalNumStrs.indexOf(variable.goal)==-1) {
				goalNumStrs.push(variable.goal);
				goals[''+variable.goal] = [];
			}
			goals[''+variable.goal].push(variable);
		});
		
		for(var i=0, _g=goalNumStrs.length; i<_g; i++) {
		    goalNums.push(+goalNumStrs[i])
		}
		goalNums = goalNums.sort();
		
		var tb = $("<tbody />");
		var mH = 'mdg_header';
		$.each(goalNums.sort(), function(i, gn){
			var thR = $("<tr />", {'class': 'mdg-header'});
			thR.append($("<td />", {'class':mH, colspan: 3}).html(goalText[(+gn)-1]))
			$.each(years, function(yi, year){
				thR.append($("<td />", {'class': mH + ' year'}).text(year))
			});
			tb.append(thR);
			var goalsInDisplayOrder = goals[''+gn].sort(function(a,b){return a.display_order - b.display_order;})
			$.each(goalsInDisplayOrder, function(ii, gvar){
				tb.append(createRowForVariable(gvar))
			})
		});
		return $("<table />", {'class':'mdg-table f'}).html(tb);
	}
	
	$.createMdgTable = CreateMDGTable;
})(jQuery);
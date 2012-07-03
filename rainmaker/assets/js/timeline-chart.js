strServerRoot = '/';

var objTimeline = null;

// Function to add commas to integers (Read: Dollar amounts)
function addCommas(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}

function w2date(year, wn, dayNb) {
	var j10 = new Date( year,0,10,12,0,0),
		j4 = new Date( year,0,4,12,0,0),
		mon1 = j4.getTime() - j10.getDay() * 86400000;
	return new Date(mon1 + ((wn - 1)  * 7  + dayNb) * 86400000);
}

function prettyDate(objDateInput) {
	var m_names = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."];
	
	return m_names[objDateInput.getMonth()] + ' ' + objDateInput.getDate() + ', ' + objDateInput.getFullYear()
}

function timelineBox(objPaper,objParentRow) {
	var self = this;
	self.objParentRow = objParentRow;
	self.objPaper = objPaper;
	self.strBoxFill = '#CCC';
	self.active = false;
	self.year = null;
	self.week = null;
	self.datavalue = 0;
	
	self.box = null;
	self.boxcenter = new Object();

}

timelineBox.prototype.drawBox = function (numBoxX,numBoxY,numBoxWidth,numBoxHeight) {
	var self = this;
	
	self.box = self.objPaper.rect(numBoxX, numBoxY, numBoxWidth, numBoxHeight).attr({
		'fill': self.strBoxFill,
		'stroke-opacity': 0
	})
	
	//give hover if there's data in this week
	if (self.active) {
		self.box.attr('cursor','pointer');
		self.box.hover(function () {
			self.boxHover();
		});
	}
}

timelineBox.prototype.boxHover = function () {
	
	//Check scale factor in case of resize
	var numScaleFactor = this.objParentRow.objParentChart.scaleFactor;
	this.boxcenter.x = numScaleFactor * (this.box.attr('x') + (this.box.attr('width')/2));
	this.boxcenter.y = (this.box.attr('y') + (this.box.attr('height')/2));
	
	// Use old-school date formatting and month lookup because Chase is lazy
	var week = w2date(this.year, this.week, 0);
	
	var strMinDate = (week.getMonth()+1) + '/' + week.getDate() + '/' + week.getFullYear();
	var objEndDate = new Date(week.getTime() + (6*86400000)); //6 days after the week start
	var strMaxDate = (objEndDate.getMonth()+1) + '/' + objEndDate.getDate() + '/' + objEndDate.getFullYear();

	var strPopup = 'Total donations: $' + addCommas(Math.round(this.datavalue)) + '<br/><a href="#table_top" onClick="showDateRange(\'' + strMinDate + '\',\'' + strMaxDate + '\');">Show this week\'s donations</a> ';

	closeHoverBox();
	$('#contribution-timeline').append('<div id="timeline-hover-marker"><div>');
	
	$('#timeline-hover-marker').css({
		'left':this.boxcenter.x,
		'top':(this.boxcenter.y-3)
	});
	
	$('#timeline-hover-marker').popover({
		'placement': 'top',
		'title':'<button class="close" onClick="closeHoverBox();">&times;</button>Week of ' + prettyDate(week),
		'content':strPopup,
		'trigger':'manual'
	});
	$('#timeline-hover-marker').popover('show');

}

function closeHoverBox() {
	$('#timeline-hover-marker').popover('hide');
	$('#timeline-hover-marker').remove();
}

function showDateRange(minDate,maxDate) {
	minDateFilter = new Date(minDate).getTime();
	maxDateFilter = new Date(maxDate).getTime();

	$("#contribution-list h1").html('List of contributions (' + prettyDate(new Date(minDate)) + ' to ' + prettyDate(new Date(maxDate)) + ') <a href="Javascript:clearDates();">Clear dates</a>');
	oTable.fnDraw();
	closeHoverBox();
}

function clearDates() {
	minDateFilter = undefined;
	maxDateFilter = undefined;
	$("#contribution-list h1").html('List of contributions');
	oTable.fnDraw();
}

function timelineRow (objPaper,objParentChart) {
	var self = this;
	self.objParentChart = objParentChart;
	self.objPaper = objPaper;
	self.numWidth = 280;
	self.numHeight = 15;
	self.numX = 0;
	self.numY = 0;
	self.numXPadding = 1;
	self.numLeftPadding = 20;
	self.objYearData = null;
	self.numFontSize = 11;	

	self.numBoxWidth = 10;
	self.numBoxHeight = 10;
	
	self.numGreatestDonationLevel = 1000000;
	
	self.boolColorMode = true;
	
	//if grayscale mode
	self.numGreatestColorValue = 210;
	self.numLowestColorValue = 0;
	
	//if hsb color mode
	self.numHueDegrees = 26;
	self.pctGreatestColorSat = 100;
	self.pctLowestColorSat = 5;
	self.pctBrightness = 90;

	self.objLabel = null;
	
	self.objBoxes = [];
	
}

timelineRow.prototype.drawLabel = function () {
	this.objLabel = this.objPaper.text(0, this.numY + this.numFontSize/2, this.objYearData.numYear).attr({
		'text-anchor': 'start',
		'font-size': this.numFontSize
	});
}

timelineRow.prototype.generateHSLShade = function (numHue,pctSaturation,pctBright) {
	//get hue pct
	var pctHue = numHue/360;
	
	var hexColor = Raphael.hsb(pctHue,pctSaturation/100,pctBright/100);
	
	return hexColor;
}

timelineRow.prototype.drawBoxes = function () {
	var self = this;
	var numRowOrigin = this.numLeftPadding;
	
	for (var numWeek=1; numWeek <= 53; numWeek ++) {
		//default color
		var strFillColor = '#F2F2F2';

		var objBox = new timelineBox(self.objPaper,self);
		objBox.week = numWeek;
		objBox.year = self.objYearData.numYear;

		//check for donations in this week
		$.each(this.objYearData.weeks, function(numWeekKey, objWeek) {
			if (objWeek.week == numWeek) {
				
				var numDonationTotal = objWeek.total;
				objBox.active = true;
				objBox.datavalue = numDonationTotal;
				
				if (self.boolColorMode) {
					//choose hsb shade by manipulating saturation as percentage of min/max color value and donation
					var pctSaturation = Math.floor(self.pctLowestColorSat + ((numDonationTotal/self.numGreatestDonationLevel) * (self.pctGreatestColorSat-self.pctLowestColorSat)));			
					if (pctSaturation > self.pctGreatestColorSat) {
						pctSaturation = self.pctGreatestColorSat;
					}
					strFillColor = self.generateHSLShade(self.numHueDegrees,pctSaturation,self.pctBrightness);
					
				} else {
					//figure correct rbg gray shade based on proportion of max donation vs. min/max color range
					var numColorValue = self.numGreatestColorValue - Math.floor((numDonationTotal*self.numGreatestColorValue)/self.numGreatestDonationLevel);
					
					strFillColor = 'rgb(' + numColorValue + ', ' + numColorValue + ', ' + numColorValue + ')';
				}				
			}
		});
		
		var numBoxX = numRowOrigin + (numWeek*(self.numBoxWidth+self.numXPadding));
		
		objBox.strBoxFill = strFillColor;		
		objBox.drawBox(numBoxX, self.numY, self.numBoxWidth, self.numBoxHeight);
		self.objBoxes.push(objBox);
			
	}
}

function timelineChart (strTarget, numChartWidth, numChartHeight, objJSON) {
	var self = this;
	
	self.strContainerName = strTarget;
	//to access Raphael stuff
	self.objPaper = ScaleRaphael(strTarget,numChartWidth,numChartHeight);
	self.objPaper.clear();
	
	self.nativeWidth = numChartWidth;
	self.nativeHeight = numChartHeight;
	self.scaleFactor = 1;
      
	self.years = [];
	self.objJSON = objJSON;
	
	self.minYear = 2001;
	self.maxYear = 2011;
	
}

function resizePaper(){
	var objPaperContainer = $('#contribution-timeline');
	
	if ($(window).width() < 960) {
		objTimeline.scaleFactor = objPaperContainer.width()/objTimeline.nativeWidth;
		objTimeline.objPaper.changeSize(objPaperContainer.width(), Math.ceil(objTimeline.nativeHeight*objTimeline.scaleFactor), false, false);
		
	} else {
		objTimeline.scaleFactor = 1;
		objTimeline.objPaper.changeSize(objTimeline.nativeWidth,objTimeline.nativeHeight, false, false);
	}
}


timelineChart.prototype.drawChart = function () {
	var self = this;
	
	for (var numYear = self.minYear; numYear <= self.maxYear; numYear++) {
		var boolYearMatch = false;
		
		var objEmptyYear = {
			'numYear': numYear,
			weeks: []
		}
		
		var objRow = new timelineRow(self.objPaper,self);
		objRow.numY = (numYear-self.minYear)*objRow.numHeight;
		objRow.objYearData = objEmptyYear;

		$.each(self.objJSON, function(numKey, objYear) {
			if (objYear.numYear == numYear) {
				objRow.objYearData = objYear;
			}
		});

		objRow.drawLabel();
		objRow.drawBoxes();
		
		self.years.push(objRow);
	}
	//add key to bottom
	$('#' + self.strContainerName).append('<div id="start-week-label">Jan.</div><div id="end-week-label">Dec.</div>');
	//override overflow:hidden set by Raphael canvas
	$('#' + self.strContainerName).css('overflow','visible');
}

function buildTimeline(strSlug,strTargetID) {
	//progress wheel
	$('#contribution-timeline').append('<div class="progress-wheel"><img class="wheel" src="http://media.apps.cironline.org/rainmaker/site_media/image/progress-wheel-30.gif" width="30" height="30"/>Loading timeline ...</div>');
	
	$.getJSON(strServerRoot + 'json/timeline/' + strSlug + '/', function(objYears) {
		$('#' + strTargetID).html('');
		objTimeline = new timelineChart(strTargetID,615,180,objYears);

		resizePaper();
		$(window).resize(resizePaper);
		
		closeHoverBox();
		objTimeline.drawChart();
		
		//remove progress wheel
		$('#contribution-timeline .progress-wheel').remove();
	});
}

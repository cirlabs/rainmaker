(function() {
	
	var strServerRoot = 'http://rainmaker.apps.cironline.org';
	var trackingTimer;
	
	var jQuery;

	/******** Load jQuery if not present *********/
	if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.7.1') {
		var script_tag = document.createElement('script');
		script_tag.setAttribute("type","text/javascript");
		script_tag.setAttribute("src",
			"http://media.apps.cironline.org/shared/bootstrap/js/jquery.js");
		if (script_tag.readyState) {
		  script_tag.onreadystatechange = function () { // For old versions of IE
			  if (this.readyState == 'complete' || this.readyState == 'loaded') {
				  scriptLoadHandler();
			  }
		  };
		} else { // Other browsers
		  script_tag.onload = scriptLoadHandler;
		}
		// Try to find the head, otherwise default to the documentElement
		(document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
	} else {
		// The jQuery version on the window is the one we want to use
		jQuery = window.jQuery;
		main();
	}
	
	/******** Called once jQuery has loaded ******/
	function scriptLoadHandler() {
		// Restore jQuery and window.jQuery to their previous values and store the
		// new jQuery in our local jQuery variable
		jQuery = window.jQuery.noConflict(true);
		$ = window.jQuery;
		// Call our main function
		main(); 
	}
	
	/******** Our main function ********/
	function main() { 

		var arrCSSLinks = [];
		arrCSSLinks.push("http://media.apps.cironline.org/rainmaker/site_media/css/widget.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/bootstrap/css/bootstrap.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/bootstrap/css/bootstrap-responsive.css");
		arrCSSLinks.push("http://media.apps.cironline.org/shared/cawatch-responsive/cawatch-bootstrap-reset.css");
		
		/******* Load CSS *******/
        jQuery.each(arrCSSLinks, function (numKey, objItem) {
			var css_link = jQuery("<link>", { 
				rel: "stylesheet", 
				type: "text/css", 
				href: objItem
			});
			css_link.appendTo('head');
        });
                        
		/******* Load HTML *******/
		jQuery(document).ready(function(jQuery) { 
			var strTabs = '<ul id="main-tab" class="nav nav-tabs"><li class="active"><a href="#indiv-tab">Top 10 individuals</a></li><li><a href="#group-tab">Top 10 groups</a></li></ul>';
			
			var boolHed = true;
			var boolDescription = true;
			if (typeof rainmaker_exclude === 'undefined') {
				boolHed = true;
				boolDescription = true;
			} else {
				if (jQuery.inArray('headline',rainmaker_exclude) != -1) {
					boolHed = false;
				}
				if (jQuery.inArray('description',rainmaker_exclude) != -1) {
					boolDescription = false;
				}
			}
				
			if (boolHed) {
				jQuery('#rainmaker-widget-container').append('<h2 id="widget-hed"><strong>The Rainmakers:</strong> California\'s top political donors, 2001-2011</h2>');
			}
			
			if (boolDescription) {
				jQuery('#rainmaker-widget-container').append('<p id="widget-intro">Lavishing their largesse on legislators and political committees alike, <a href="http://californiawatch.org/money-and-politics/states-top-100-political-donors-contribute-125-billion-16436">the largest donors to California politics spent $1.25 billion from 2001 through 2011</a>. The group &ndash; 50 special interests and 50 wealthy individuals &ndash; spans the Golden State\'s social order. They are corporate leaders and venture capitalists, real estate developers and Hollywood scions. They are energy and tobacco companies, labor unions and tribal governments. Collectively, they shelled out a third of all the money given to campaigns in the state during the 11-year period.');
			}
			
			jQuery('#rainmaker-widget-container').append('<div id="widget-logo">Produced by <a href="http://rainmaker.apps.cironline.org/" target="_blank"><img src="http://media.apps.cironline.org/shared/img/cawatch-logo-226x27.png" width="226" height="27" border="0"/></a></div>');
			
			jQuery('#rainmaker-widget-container').append(strTabs);
			
			jQuery('.nav-tabs li a').click(function (e) {
				e.preventDefault();
				jQuery('.nav-tabs li').removeClass('active');
				jQuery(this).parent('li').addClass('active');
				
				jQuery('.tab-content .tab-pane').removeClass('active');

				var strTabTarget = jQuery(this).attr('href');
				jQuery(strTabTarget).addClass('active');
				
			});
			
			jQuery('#rainmaker-widget-container').append('<div class="tab-content"><div class="tab-pane active" id="indiv-tab"></div><div class="tab-pane" id="group-tab"></div></div>');
			
			var objIndivTable = new donorTable('#indiv-tab','individuals');
			var objGroupTable = new donorTable('#group-tab','groups');
			
			doGATracking();
		});
	}
	
	function donorTable(strTarget,strType) {
		var self = this;
		
		var strTypeCode;
		if (strType == 'individuals') {
			strTypeCode = 'I';
		} else {
			strTypeCode = 'C';
		}
		
		self.strTarget = strTarget;
		self.strType = strType;
		self.strTypeCode = strTypeCode;
		
		self.drawTopTen();
	}
	
	donorTable.prototype.drawTopTen = function () {
		var self = this;
		
		var jsonp = jQuery.getJSON(strServerRoot + '/api/v1/donor/?type=' + self.strTypeCode + '&offset=0&limit=10&format=jsonp&callback=?', function(data) {
			var strRows = '';
			jQuery.each(data.objects, function(numKey, objDonor) {
				strRows += '<tr>';
				strRows += '<td class="rank">' + objDonor.rank + '</td>';
				
				var strPhoto = '';
				if (objDonor.image != null) {
					strPhoto = '<img class="mug" src="http://media.apps.cironline.org/rainmaker' + objDonor.image + '" width="50"/>';
				}
				
				strRows += '<td class="donor">' + strPhoto + '<div class="donor-name"><a href="' + objDonor.full_url + '" target="blank">' + objDonor.name + '</a></div><div class="donor-location">' + objDonor.location_city + ', ' + objDonor.location_state + '</div><div class="donor-descrip">' + objDonor.line_of_work + '</div><div class="donor-stats">' + addCommas(objDonor.total_contributions_count) + ' donations: ' + addCommas(objDonor.candidate_contributions_count) + ' to candidates, ' + addCommas(objDonor.ballot_contributions_count) + ' to ballot measures and ' + addCommas(objDonor.party_contributions_count) + ' to parties</div></td>';
				strRows += '<td class="amount">$' + addCommas(Math.round(objDonor.contribs_sum)) + '</td>';
				strRows += '</tr>';
			});
			
			var strTable = '<table class="donor-list" cellpadding="0" cellspacing="0" border="0">' + strRows + '</table>';
			jQuery(self.strTarget).html(strTable);
			
		});
	}
		
	function doGATracking() {
		//check if analytics running
		if (!window._gat) {
			var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
			
			var script = document.createElement( 'script' );
			script.type = 'text/javascript';
			script.src = gaJsHost + "google-analytics.com/ga.js";
			document.getElementById('rainmaker-widget-container').appendChild(script);
			
		}
		
		tryTracking();
		
	}
		
	function addCommas(nStr) {
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
})();

var widgetTracker;

function tryTracking() {
	try {
	   widgetTracker = _gat._getTracker("UA-2147301-15"); // CIR news apps account
	   widgetTracker._trackEvent('Widgets', 'rainmaker widget load', location.href);
	   
	   clearTimeout(trackingTimer);
	   
	} catch(err){
		trackingTimer = setTimeout('tryTracking()',500);	
	}
}

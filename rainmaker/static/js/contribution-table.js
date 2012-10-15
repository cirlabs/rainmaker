var strServerRoot = '/'; //local
var oTable;
//date filtering
var minDateFilter;
var maxDateFilter;

function writeTable(strDonorID) {

	//progress wheel
	$('#contribution-list').append('<div class="progress-wheel"><img class="wheel" src="http://media.apps.cironline.org/rainmaker/site_media/image/progress-wheel-30.gif" width="30" height="30"/>Loading table ...</div>');
	
	$.getJSON(strServerRoot + 'api/v1/donor-contributions/' + strDonorID + '/?format=json', function(data) {
	
		var strTableHeader = '<thead><tr><th class="date">Date</th><th class="recipient">Recipient</th><th class="amount">Amount</th><th class="hidden-td">is ballot?</th><th class="hidden-td">is candidate?</th><th class="hidden-td">is committee?</th><th class="hidden-td">is winner?</th><th class="hidden-td">is loser?</th></tr></thead>';
		
		var strTableRows = '';
		$.each(data.contributions, function(numKey, objRow) {
			var strTDs = '';
			if (!objRow.date) {
				strDate = '';
			} else {
				//parse date
				arrDate = objRow.date.split('-');
				strDate = prettyDate(new Date(Number(arrDate[0]),Number(arrDate[1])-1,Number(arrDate[2])));
			}
			
			//interestingness
			var strInteresting = '';
			if (objRow.bool_interesting) {
				strInteresting = '<div class="interesting">Beta: Interesting contribution <a href="#">What\'s this?</a></div>';
			}


			strTDs += '<td class="date">' + strDate + '</td>';
			strTDs += '<td class="recipient">';
			strTDs += '<div>'+ objRow.recipient + '</div>';
			for (numE=0; numE < objRow.explainers.length; numE++) {
				if (objRow.explainers[numE].winner) {
					strResultClass= 'win';
				} else {
					strResultClass= 'loss';
				}
				
				strTDs += '<div>' + objRow.explainers[numE].text + ' <span class="' + strResultClass + '">' + objRow.explainers[numE].outcome_text + '</span></div>';
			}
			strTDs += strInteresting;
			strTDs += '</td>';
 			strTDs += '<td class="amount">$' + addCommas(objRow.amount) + '</td>';
 			strTDs += '<td class="hidden-td">' + objRow.bool_ballot + '</td>';
 			strTDs += '<td class="hidden-td">' + objRow.bool_candidate + '</td>';
 			strTDs += '<td class="hidden-td">' + objRow.bool_committee + '</td>';
 			strTDs += '<td class="hidden-td">' + objRow.bool_win + '</td>';
 			strTDs += '<td class="hidden-td">' + objRow.bool_loss + '</td>';
						
			strTableRows += '<tr>' + strTDs + '</tr>';
		});

		$('#contribution-list').append('<table id="myTable">' + strTableHeader + '<tbody>' + strTableRows + '</tbody></table>');
		parseTable();
		$('#contribution-list .progress-wheel').remove();
	});
}


/* add leading zeros */
function pad(number, length) {
	var str = '' + number;
	while (str.length < length) {
		str = '0' + str;
	}
	return str;
}

/*Getting month index value*/
function getMonthIdx(monthName) {
	var months = {
		'Jan.':0, 'Feb.':1, 'March':2, 'April':3, 'May':4, 'June':5, 'July':6, 'Aug.':7, 'Sept.':8, 'Oct.':9, 'Nov.':10, 'Dec.':11
	};
	return months[monthName];
}


function checkFilter(objTarget,numColumn) {
	var bool = 'false';
	if (objTarget.checked) {
		/* Filter on the column (the index) of this element */
		oTable.fnFilter('', numColumn);
	} else {
		oTable.fnFilter( bool, numColumn);
	}				
}

function parseTable() {
	// Custom date sorting functions for ascending sorting of dates in "MMM dd yyyy" format*/

	oTable = $('#myTable').dataTable({
		"sDom": 'f<"toolbar">tipr',
		"sPaginationType": "full_numbers",
		"aaSorting": [[ 2, "desc" ]],
		"iDisplayLength": 25,
		"oLanguage": {
			"sSearch": "Filter contributions"
		},
		"aoColumns": [
			{ "sSortDataType": "dom-text", "sType": "date-custom" },
			null,
			{ "sSortDataType": "dom-text", "sType": "currency" },
			null,
			null,
			null,
			null,
			null
		],
		"fnPreDrawCallback": function( oSettings ) {
			$('#myTable tbody tr').css('display','none');
		},
		"fnDrawCallback": function( oSettings ) {
			$('#myTable tbody tr').fadeIn();
			$('.interesting a').popover({
				'placement': 'top',
				'title':'Interestingness',
				'content':'This beta feature indicates contributions that are unusual based on absolute and relative dollar amount, the partisan giving history of the donor, the donor\'s historical relationship to the recipient and other factors.'
			});
		}
	});
	
	$("div.toolbar").html('<span id="type-check-group"><h4>Show donations to</h4><input id="candidate_checkbox" type="checkbox" checked="checked"/> Candidates &nbsp;&nbsp;<input id="party_checkbox" type="checkbox" checked="checked"/> Committees</span><span id="result-check-group"><span style="display:none"><h4>Results</h4><input id="win_checkbox" type="checkbox" checked="checked"/> Wins &nbsp;&nbsp;<input id="loss_checkbox" type="checkbox" checked="checked"/> Losses</span></span>');
		
	jQuery.fn.dataTableExt.afnFiltering.push(
	  function( oSettings, aData, iDataIndex ) {
		
		//filter out no date
		if (aData[0] == 'None') {
			return false;
		}
		
		if ( typeof aData._date == 'undefined' ) {
		  aData._date = new Date(aData[0]).getTime();
		}
		
		if ( minDateFilter && !isNaN(minDateFilter) ) {
		  if ( aData._date < minDateFilter ) {
			return false;
		  }
		}
		
		if ( maxDateFilter && !isNaN(maxDateFilter) ) {
		  if ( aData._date > maxDateFilter ) {
			return false;
		  }
		}
		
		return true;
	  }
	);
	//end date filtering
	
	$("#ballot_checkbox").click(function () {
		checkFilter(this,3);
	});
	
	$("#candidate_checkbox").click(function () {
		checkFilter(this,4);
	});
	
	$("#party_checkbox").click(function () {
		checkFilter(this,5);
	});
	
	//win/loss filter
	jQuery.fn.dataTableExt.afnFiltering.push(
	  function( oSettings, aData, iDataIndex ) {
		var iWinCol = 6;
		var iLossCol = 7;
		
		var boolShow = false;
		
		var strWinData = aData[iWinCol];
		var strLossData = aData[iLossCol];
		
		if ($("#win_checkbox").is(':checked')) {
			if (strWinData != 'false') {
				boolShow = true;
			}
		}
		
		if ($("#loss_checkbox").is(':checked')) {
			if (strLossData != 'false') {
				boolShow = true;
			}
		}
	
		return boolShow;
	  }
	);
	
	
	$("#win_checkbox").click(function () {
		oTable.fnDraw();
	});
	
	$("#loss_checkbox").click(function () {
		oTable.fnDraw();
	});
}

(function( $ ) {
	jQuery.fn.dataTableExt.oSort['date-custom-asc'] = function(a,b) {
		// Making sure to remove any HTML code sorrounding the value to be sorted.
		var date1 = a.replace( /<.*?>/g, "" ).replace(/,/g,"").replace(/^\s+|\s+$/g,"");
		var date2 = b.replace( /<.*?>/g, "" ).replace(/,/g,"").replace(/^\s+|\s+$/g,"");
		
		//Split date fields on white space to get MMM, dd and YYYY as array
		var dateTokens1 = date1.split(' ');
		var dateTokens2 = date2.split(' ');
		
		var x = (dateTokens1[2] + pad(getMonthIdx(dateTokens1[0]),2) + pad(dateTokens1[1],2)) * 1;
		var y = (dateTokens2[2] + pad(getMonthIdx(dateTokens2[0]),2) + pad(dateTokens2[1],2)) * 1;
		
		return ((x < y) ? -1 : ((x > y) ? 1 : 0));
	};
	
	// Custom date sorting functions for descending sorting of dates in "MMM dd yyyy" format*/
	jQuery.fn.dataTableExt.oSort['date-custom-desc'] = function(a,b) {
		// Making sure to remove any HTML code sorrounding the value to be sorted.
		var date1 = a.replace( /<.*?>/g, "" ).replace(/,/g,"").replace(/^\s+|\s+$/g,"");
		var date2 = b.replace( /<.*?>/g, "" ).replace(/,/g,"").replace(/^\s+|\s+$/g,"");
		
		//Split date fields on white space to get MMM, dd and YYYY as array
		var dateTokens1 = date1.split(' ');
		var dateTokens2 = date2.split(' ');
		
		var x = (dateTokens1[2] + pad(getMonthIdx(dateTokens1[0]),2) + pad(dateTokens1[1],2)) * 1;
		var y = (dateTokens2[2] + pad(getMonthIdx(dateTokens2[0]),2) + pad(dateTokens2[1],2)) * 1;
						
		return ((x < y) ? 1 : ((x > y) ? -1 : 0));
	};
	
	
	jQuery.fn.dataTableExt.oSort['currency-asc'] = function(a,b) {
		/* Remove any formatting */
		var x = a == "-" ? 0 : a.replace( /[^\d\-\.]/g, "" );
		var y = b == "-" ? 0 : b.replace( /[^\d\-\.]/g, "" );
		 
		/* Parse and return */
		x = parseFloat( x );
		y = parseFloat( y );
		return x - y;
	};
	 
	jQuery.fn.dataTableExt.oSort['currency-desc'] = function(a,b) {
		var x = a == "-" ? 0 : a.replace( /[^\d\-\.]/g, "" );
		var y = b == "-" ? 0 : b.replace( /[^\d\-\.]/g, "" );
		 
		x = parseFloat( x );
		y = parseFloat( y );
		return y - x;
	};
	
})( jQuery );

	// If the browser is Firefox get the version number
	var ffv = 0;
	var ffn = "Firefox/"
	var ffp = navigator.userAgent.indexOf(ffn);
	if (ffp != -1) ffv = parseFloat(navigator.userAgent.substring(ffp + ffn.length));
	// If we're using Firefox 1.5 or above override the Virtual Earth drawing functions to use SVG
	if (ffv >= 1.5) {
  		Msn.Drawing.Graphic.CreateGraphic=function(f,b) { return new Msn.Drawing.SVGGraphic(f,b) }
	}
	// Put your own code below this line
		var map = null;
		
		var poopons = new Array();
		var pooponslength = 0;
		function GetMap() {
			map = new VEMap('myMap');
			map.LoadMap(new VELatLong(52.4997, 0.19134), 14 ,'h' ,false);
			map.AttachEvent("onclick", MouseClick);
			printWaypoints();			
		}
		
		var pid = 1;
		var RouteId = 1;
		function VERoute(Waypoints, RouteId) {

			this.latlongs = new Array();
			for ( var pid in poopons ) {
					niceobj = poopons[ pid ];
					this.latlongs.push(  new VELatLong( niceobj.lat ,niceobj.lon ) ) ;
				
			}
			this.poly = new VEPolyline(RouteId,this.latlongs);
			this.poly.SetWidth(1);
			this.poly.SetColor(new VEColor(250,250,50,1.0) );

	
		}
		function WayPointSet() {
			this.waypoints = new Array();
			this.waypointslength = 0;
		}
		function WayPoint(lato,longo,pid,pname) {
			this.lon = longo;
			this.lat = lato;
			this.pid = pid;
			this.getLat = function() {
				return this.lat;
			};
			this.getLon = function() {
				return this.lon;
			};
			if ( pname ) {
				this.pname = pname;
			} 
			else {
				this.pname = 'My Pushpin' + pid;
			}
			this.pdesc = 'My Pushpin' + 'This is pushpin number ' + pid;
			
			this.printWayPointXML = function() {
			
				this.wpxml  = '<wpt lat="' + this.lat + '" lon="' + this.lon + '">\n';
				this.wpxml += '<name>' + this.pname + '</name>\n';
				this.wpxml += '<cmt>' + this.pname + '</cmt>\n';
				this.wpxml += '<desc>' + this.pname + '</desc>\n';
				this.wpxml += '<sym>WayPoint</sym>\n';
				this.wpxml += '</wpt>\n';
				return this.wpxml;
			
			};
		}
		function MouseClick(e) {
			
			var longi = e.view.LatLong.Longitude;
			var lati = e.view.LatLong.Latitude;
			var pin = new VEPushpin(
				pid, 
				new VELatLong(
					e.view.LatLong.Latitude, 
					e.view.LatLong.Longitude
				), 
				null,
				'My pushpin ' + pid, 
				'This is pushpin number '+pid
			);

			var wp = new WayPoint(
				e.view.LatLong.Latitude,
				e.view.LatLong.Longitude,
				pid,
				0
			);

			map.AddPushpin(pin);

			//add pushpin details to my array
			poopons[ 'id'+pid ] = wp;
			pooponslength += 1;
			/* 
			document.getElementById("info").innerHTML =
			'monky'+wp.getLat();
			what we need here is a waypoint class with an
			attribute linked to the pushpin id */
			//pass the waypoint object to the
				
			pid += 1;
			printWaypoints();
		}
		function DeletePushpin(aform)
		{
			var pid2go = aform.pid.value;
			map.DeletePushpin( pid2go );
			delete poopons[ 'id'+pid2go ];


			pooponslength -= 1;
			
			printWaypoints();			
		}
		function DelAll(aform) 
		{

			map.DeleteAllPushpins();
			var poopons=new Array();
			pooponslength = 0;
			printWaypoints();		
		}
		function UpdatePushpin(aform)
		{
			var pid2go = aform.pid.value;
			map.DeletePushpin( pid2go );
			delete poopons[ 'id'+pid2go ];

			var upin = new VEPushpin(
				pid2go, 
				new VELatLong(
					aform.latbox.value, 
					aform.lonbox.value
				), 
				null,
				aform.title.value, 
				'This is pushpin number ' + pid2go
			);
			map.AddPushpin(upin);
			var uwp = new WayPoint(
					aform.latbox.value,
					aform.lonbox.value,
					pid2go,
					aform.title.value
					
			);
			poopons[ 'id'+pid2go ] = uwp;
			
			printWaypoints();			
		}
		function makeRoute() {
			if ( pooponslength > 0 ) {
			
				aroute = new VERoute(poopons,RouteId);
				map.AddPolyline(aroute.poly);
				RouteId +=1;
			}
		
		}
		
		function printWaypoints()
		{
				
			var inhtml = '';
			// alert( poopons.length)
			if ( pooponslength > 0 ) {

				for ( var pid in poopons ) {
					niceobj = poopons[ pid ];

					inhtml += '<FORM NAME="myform" ACTION="" METHOD="GET">';
					inhtml += '<fieldset>';
					inhtml += 'WayPoint ' + niceobj.pid +' ';
					inhtml += Math.round( niceobj.lat * 10000 ) / 10000 + ', ' + Math.round( niceobj.lon*10000 ) / 10000 +' ';
					inhtml += '<INPUT TYPE="hidden" NAME="pid" VALUE="'+niceobj.pid+'"/>';
					inhtml += '<INPUT TYPE="hidden" class="textbox" NAME="latbox" VALUE="' + niceobj.lat + '"/>';
					inhtml += '<INPUT TYPE="hidden" class="textbox" NAME="lonbox" VALUE="' + niceobj.lon + '"/>';
					inhtml += '<INPUT TYPE="text" class="textbox" NAME="title" VALUE="' + niceobj.pname + '"/>';
					inhtml += '<INPUT TYPE="button" NAME="updatebutton" Value="Update" onClick="UpdatePushpin(this.form)"/>';
					inhtml += '<INPUT TYPE="button" NAME="deletebutton" Value="Delete" onClick="DeletePushpin(this.form)"/>';

					inhtml +='</fieldset>';
					inhtml +=  '</FORM>';

					}
				inhtml += '<FORM NAME="process" ACTION="" METHOD="GET">';
				inhtml += '<INPUT TYPE="button" NAME="delallbutton" Value="Del All" onClick="DelAll(this.form)"/>';
				inhtml += '<INPUT TYPE="button" NAME="xmlbutton" Value="XML" onClick="DoXML(this.form)"/>';
					inhtml += '<INPUT TYPE="button" NAME="routebutton" Value="Route-O-Mat" onClick="makeRoute(this.form)"/>';
				
				inhtml +=  '</FORM>';

			}
			else{
				inhtml = '<p class="waffle">No WayPoints selected... Go clicking!</p>';							
			}
			
			document.getElementById("info").innerHTML =inhtml;
			//alert(inhtml);
			
		}
		//leverage ShowFindControl and ShowMessage
		function DoXML() {
			var xmldoc = '<?xml version="1.0" encoding="UTF-8"?>\n'
			xmldoc += '<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="Link2GPS - 2.0.2 - http://www.hiketech.com" xsi:schemaLocation="ttp://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n';
			for ( waypointid in poopons ) {
				wayhey = poopons[ waypointid ];
				xmldoc += wayhey.printWayPointXML();
			}
			xmldoc += '</gpx>';
			var srcwin = window.open("about:blank","","menubar,height=800,width=600,resizable,scrollbars");
			srcwin.document.open ('content-type: text/xml');
			srcwin.document.write(xmldoc);
			srcwin.document.close();

		}

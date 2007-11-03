from xml.dom import pulldom
print pulldom.__name__
gpxlog = pulldom.parse('yorkshire.gpx')
for event,node in gpxlog:
    # Only construct a dom from the track points
    if event == 'START_ELEMENT' and node.nodeName == 'trkpt':
        # we can expand the node to use the DOM API
        gpxlog.expandNode(node)
        # We only want track points with a time stamp
        if node.getElementsByTagName('time'):
            timenode = node.getElementsByTagName('time')
            elenode = node.getElementsByTagName('ele')
            timestring = timenode[0].firstChild.nodeValue
            elestring = elenode[0].firstChild.nodeValue
        else: 
            pass # This is not a active log way point
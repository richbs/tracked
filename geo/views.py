# Create your views here.
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import Template, Context, loader
from tracked.geo.models import WayPoint


def dates(request,date_from,date_to):

    t = loader.get_template('dates.html')
    df = datetime.strptime(date_from, '%Y%m%d')
    oneday = timedelta(days=1)
    dt = datetime.strptime(date_to, '%Y%m%d')
    dt = dt + oneday
    waypoints = WayPoint.objects.filter(time__gte=df).filter(time__lte=dt).order_by('time')
    c = Context({
        'waypoints': waypoints
    })
    return HttpResponse(t.render(c))
    
import shutil
from django.conf import settings
from django.test import TestCase
from geo.models import GpxFile, WayPoint, Track


class GpxTest(TestCase):

    def setUp(self):

        filename = settings.BASE_PATH + '/geo/data/yorkshire.gpx'
        g = GpxFile()
        shutil.copyfile(filename, settings.MEDIA_ROOT + '/xml/yorkshire.gpx')
        g.filename = 'xml/yorkshire.gpx'
        g.save()

    def test_waypoints(self):
        gpx = GpxFile.objects.all()[0]
        gpx.name = 'My Year Trip'
        gpx.save()
        self.assertGreater(gpx.waypoints.count(), 0)

import shutil
from django.conf import settings
from django.test import TestCase
from geo.models import GpxFile, WayPoint, Track


class GpxTest(TestCase):

    def setUp(self):

        filename = settings.BASE_PATH + '/geo/data/yorkshire.gpx'
        g = GpxFile()
        g.name = "Tester"
        shutil.copyfile(filename, settings.MEDIA_ROOT + '/xml/yorkshire.gpx')
        g.filename = 'xml/yorkshire.gpx'
        g.save()

    def test_waypoints(self):
        gpx = GpxFile.objects.all()[0]
        gpx.name = 'My Year Trip'
        gpx.save()
        self.assertGreater(gpx.waypoints.count(), 0)


class ViewTest(TestCase):

    def setUp(self):

        filename = settings.BASE_PATH + '/geo/data/yorkshire.gpx'
        g = GpxFile()
        g.name = "Tester"
        shutil.copyfile(filename, settings.MEDIA_ROOT + '/xml/yorkshire.gpx')
        g.filename = 'xml/yorkshire.gpx'
        g.save()

    def test_home(self):

        response = self.client.get('/')
        self.assertContains(response, "Where have", 1, 200)

    def test_track(self):
        response = self.client.get('/track/1')
        self.assertContains(response, 'Distance', 1, 200)

        response = self.client.get('/os-track/1')
        self.assertContains(response, 'Trip: Tester', 1, 200)

from django.conf import settings
from django.test import TestCase
from geo.models import GpxFile, WayPoint, Track


class GpxTest(TestCase):

    def test_import(self):

        filename = settings.BASE_PATH + '/geo/data/yorkshire.gpx'
        print filename
        g = GpxFile()
        g.process_gpx_file(filename)


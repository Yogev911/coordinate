class Point():
    def __init__(self, latitude=None, longitude=None, altitude=None):
        if latitude and longitude and altitude:
            self.latitude = float(str(latitude))
            self.longitude = float(str(longitude))
            self.altitude = float(str(altitude))


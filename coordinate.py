from fpformat import fix
from math import radians, cos, sin, asin, atan2, degrees, sqrt, atan, tan, acos

from point import Point

EARTH_RADIUS = 6371e3


def get_point(coord_a, distance, azimuth, bearing):
    # type: (Point, float, float,float) -> Point
    # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
    try:
        # Convert to radians
        alpha = radians(float(bearing))
        azimuth = radians(float(azimuth))
        coord_a.longitude = radians(coord_a.longitude)
        coord_a.latitude = radians(coord_a.latitude)
        # Calculate altitude delta
        hypotenuse = distance
        horizontal_distance = hypotenuse * cos(alpha)
        delta_alt = hypotenuse * sin(alpha)
        # Calculate latitude\longitude
        delta = horizontal_distance / EARTH_RADIUS
        final_latitude = asin(sin(coord_a.latitude) * cos(delta) +
                              cos(coord_a.latitude) * sin(delta) * cos(azimuth))
        final_longitude = coord_a.longitude + atan2(sin(azimuth) * sin(delta) * cos(coord_a.latitude),
                                                    cos(delta) - sin(coord_a.latitude) * sin(final_latitude))

        final_altitude = coord_a.altitude + delta_alt
        final_latitude = degrees(final_latitude)
        final_longitude = degrees(final_longitude)

        return Point(latitude=final_latitude, longitude=final_longitude, altitude=final_altitude)
    except Exception as e:
        raise ValueError('Cannot create point, {}'.format(e.message))


def get_relative_point_position(coord_a, coord_b):
    # type: (Point, Point) -> (float, float, float)
    try:
        # get point b distance, azimuth and elevation relative point a
        ap = _location_to_point(coord_b)
        bp = _location_to_point(coord_a)

        distance_km = fix(0.001 * _target_distance(ap, bp), 10)
        br = _rotate_globe(coord_b, coord_a, bp['radius'])
        if br['z'] * br['z'] + br['y'] * br['y'] > 1.0e-06:
            theta = degrees(atan2(br['z'], br['y']))
            azimuth = 90.0 - theta
            if (azimuth < 0.0):
                azimuth += 360.0
            if (azimuth > 360.0):
                azimuth -= 360.0
        else:
            azimuth = 0.0

        bma = _normalize_vector_diff(ap, bp)
        if bma:
            bearing = 90.0 - degrees(acos(bma['x'] * bp['nx'] + bma['y'] * bp['ny'] + bma['z'] * bp['nz']))
        else:
            bearing = 0.0
        return bearing, azimuth, distance_km
    except:
        pass


def _location_to_point(point):
    lat = radians(point.latitude)
    lon = radians(point.longitude)
    t1 = 6378137.0 * 6378137.0 * cos(lat)
    t2 = 6356752.3 * 6356752.3 * sin(lat)
    t3 = 6378137.0 * cos(lat)
    t4 = 6356752.3 * sin(lat)
    radius = sqrt((t1 * t1 + t2 * t2) / (t3 * t3 + t4 * t4))
    clat = atan((1.0 - 0.00669437999014) * tan(lat))

    cosLon = cos(lon)
    sinLon = sin(lon)
    cosLat = cos(clat)
    sinLat = sin(clat)
    x = radius * cosLon * cosLat
    y = radius * sinLon * cosLat
    z = radius * sinLat
    cosGlat = cos(lat)
    sinGlat = sin(lat)
    nx = cosGlat * cosLon
    ny = cosGlat * sinLon
    nz = sinGlat
    x += point.altitude * nx
    y += point.altitude * ny
    z += point.altitude * nz
    return {'x': x, 'y': y, 'z': z, 'radius': radius, 'nx': nx, 'ny': ny, 'nz': nz}


def _target_distance(point_a, point_b):
    dx = point_a['x'] - point_b['x']
    dy = point_a['y'] - point_b['y']
    dz = point_a['z'] - point_b['z']
    return sqrt(dx * dx + dy * dy + dz * dz)


def _rotate_globe(point_b, point_a, bradius):
    br = Point(latitude=point_b.latitude, longitude=(point_b.longitude - point_a.longitude), altitude=point_b.altitude)
    brp = _location_to_point(br)
    alat = -radians(point_a.latitude)
    alat = atan((1.0 - 0.00669437999014) * tan(alat))
    acos = cos(alat)
    asin = sin(alat)
    bx = (brp['x'] * acos) - (brp['z'] * asin)
    by = brp['y']
    bz = (brp['x'] * asin) + (brp['z'] * acos)
    return {'x': bx, 'y': by, 'z': bz, 'radius': bradius}


def _normalize_vector_diff(b, a):
    dx = b['x'] - a['x']
    dy = b['y'] - a['y']
    dz = b['z'] - a['z']
    dist2 = dx * dx + dy * dy + dz * dz
    if dist2 == 0:
        return None
    dist = sqrt(dist2)
    return {'x': (dx / dist), 'y': (dy / dist), 'z': (dz / dist), 'radius': 1.0}

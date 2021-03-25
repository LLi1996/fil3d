""" for distance calculation from l, b, v
LL2018
"""

import numpy as np

R_SUN = 8.0 * 1000
THETA0 = 220  # km/s


def nearside_flatcurve_distance(l, b, v):
    """ nearside distance (inner galaxy) assuming a flat rotation curve from given l, b, v
    from Josh Peek @jegpeek

    Arguments:
        l {float} -- l
        b {float} -- l
        v {float} -- v
    Returns:
        {float} -- distance
    """

    # first let's make a ray as a function of distance and determine it's velocity
    dd = 0.01  # delta distance in pc
    maxd = 10000  # max distance in pc

    d_ray = np.arange(0, maxd, dd)
    l_ray = np.zeros_like(d_ray) + l
    b_ray = np.zeros_like(d_ray) + b

    # the is the ray of points of Galactocentric radius
    r_ray = np.sqrt((R_SUN - d_ray * np.cos(l_ray * np.pi / 180) * np.cos(b_ray * np.pi / 180)) ** 2 +
                    (d_ray * np.sin(l_ray * np.pi / 180) * np.cos(b_ray * np.pi / 180)) ** 2)

    vr_ray = np.sin(l_ray * np.pi / 180) * (R_SUN / r_ray * THETA0 - THETA0)

    if vr_ray[1] < vr_ray[0]:
        endray = np.argmin(vr_ray)
        vr_ray_trunc = vr_ray[0:endray]
        d_ray_trunc = d_ray[0:endray]
        d = np.interp(v, np.flip(vr_ray_trunc, axis=0), np.flip(d_ray_trunc, axis=0))
    if not (vr_ray[1] < vr_ray[0]):
        endray = np.argmax(vr_ray)
        vr_ray_trunc = vr_ray[0:endray]
        d_ray_trunc = d_ray[0:endray]
        d = np.interp(v, vr_ray_trunc, d_ray_trunc)

    return d

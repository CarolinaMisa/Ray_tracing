#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  things.py
#
#  Copyright 2020 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

# 2020/11/03    Move definition of Width and Height to Camera.ray_generator,
#               adapted all test routines.
#               Base_object class defined, top class for all things in scene
#               Modified test_sphere_hits to be clearer

import pylab as plt
import numpy as np
import scipy
from PIL import Image
from math import radians, tan, sqrt

from collections import OrderedDict

from rtmath import VEC3, RGB, RGB_colors, Ray, Hit, epsilon
import pdb


class Base_object:
    def __init__(self, params):
        self.params = params


    def find(self, struct, *keys):
        for el in struct:
            if el[0] == keys[0]:
                if len(keys) == 1:
                    return el[1]
                else:
                    result = self.find(el[1], *(keys[1:]))
                    if result is not None:
                        return result


    def param(self, *keys):
        return self.find(self.params, *keys)


    def __str__(self):
        return "{} {}".format(type(self).__name__, self.params)


"""
      ____
     / ___|__ _ _ __ ___   ___ _ __ __ _
    | |   / _` | '_ ` _ \ / _ \ '__/ _` |
    | |__| (_| | | | | | |  __/ | | (_| |
     \____\__,_|_| |_| |_|\___|_|  \__,_|


"""

class Camera(Base_object):
    """ Camera recibie parametros de la escana:
        - orthographic  Tipo de cámara (por defecto 'perspective')
        - look_at       Centro de la vista (VEC3)
        - location      Ubicación (VEC3)
        - angle         Ángulo de apertura horizontal (grados)
        - up
    """
    def __init__(self, params):
        super(Camera, self).__init__(params)


    def set_pixel(self, x, y, color):
        self.image.putpixel((x, y), color.as_tuple())


    def ray_generator(self, width, height):
        bg_color = RGB_colors.Black.as_tuple()
        self.image = Image.new("RGB", (width, height), bg_color)

        nr_pixels = width * height
        h_size = 2 * tan(radians(self.param('angle'))/2)
        v_size = h_size * height / width
        scale = h_size / (width - 1)

        for pix in range(nr_pixels):
            x0 = pix % width
            y0 = pix // width
            x = x0 - (width - 1)/2
            y = y0 - (height - 1)/2
            ray = Ray(self.param("location"),
                      VEC3(x * scale, y * scale, 1).normalized())
            yield ray, x0, y0

"""
     _     _       _     _
    | |   (_) __ _| |__ | |_
    | |   | |/ _` | '_ \| __|
    | |___| | (_| | | | | |_
    |_____|_|\__, |_| |_|\__|
             |___/

"""

class Light(Base_object):
    """ Luz necesita los parametros posicionales:
            (ninguno)

        Además recibie parametros de la escana:
        - location      Ubicación de la cámara (VEC3)
        - color         Color (RGB)
        - parallel      Indicador que rayos son paralelos
    """
    def __init__(self, params):
        super(Light, self).__init__(params)



"""
     _____ _     _              __ __
    |_   _| |__ (_)_ __   __ _ / /_\ \
      | | | '_ \| | '_ \ / _` | / __| |
      | | | | | | | | | | (_| | \__ \ |
      |_| |_| |_|_|_| |_|\__, | |___/ |
                         |___/ \_\ /_/
"""

class Thing(Base_object):
    def __init__(self, params):
        super(Thing, self).__init__(params)


    def intersection(self, ray):
        pass

"""
     ____        _
    / ___| _ __ | |__   ___ _ __ ___
    \___ \| '_ \| '_ \ / _ \ '__/ _ \
     ___) | |_) | | | |  __/ | |  __/
    |____/| .__/|_| |_|\___|_|  \___|
          |_|
"""

class Sphere(Thing):
    """ Sphere necesita los parametros posicionales:
            (ninguno)

        Además recibie parametros de la escana:
        - location      Ubicación de la cámara (VEC3)
        - radius        Color (RGB)
        y propiedades comunes de objetos
    """
    def __init__(self, params):
        super(Sphere, self).__init__(params)


    def get_color(self):
        return self.param("texture", "pigment", "rgb")


    def intersection(self, ray):
        location = self.param("location")
        radius = self.param("radius")

        a = 1
        b = ray.dir * (ray.loc - location) * 2
        c = abs(ray.loc - location)**2 - radius**2

        d = b*b - 4*a*c
        if abs(d) < epsilon: d = 0
        if d < 0:
            return []

        elif d == 0:
            t = -b/2
            return [Hit(t, (ray.at(t) - location).normalized(), self)]

        else:
            t1 = (-b + sqrt(d))/2
            t2 = (-b - sqrt(d))/2
            return [Hit(t1, (ray.at(t1) - location).normalized(), self),
                    Hit(t2, (ray.at(t2) - location).normalized(), self)]


"""
     ____  _
    |  _ \| | __ _ _ __   ___
    | |_) | |/ _` | '_ \ / _ \
    |  __/| | (_| | | | |  __/
    |_|   |_|\__,_|_| |_|\___|

"""

class Plane(Thing):
    """ Plane necesita los parametros posicionales:
            (ninguno)

        Además recibie parametros de la escana:
        - normal        La normal sobre la superficie (VEC3)
        - distance      Distancia del origen
        y propiedades comunes de objetos
    """
    def __init__(self, params):
        super(Plane, self).__init__(params)


    def intersection(self, ray):
        return []


"""
  _______     _                       _       
 |__   __|   (_)                     | |      
    | | _ __  _   __ _  _ __    __ _ | |  ___ 
    | || '__|| | / _` || '_ \  / _` || | / _ \
    | || |   | || (_| || | | || (_| || ||  __/
    |_||_|   |_| \__,_||_| |_| \__, ||_| \___|
                                __/ |         
                               |___/          

"""
class Triangle(Thing):
    """ Triangle recibe parametros de la escana:
            - v0        Vertice 1
            - v1        Vertice 2
            - v2        Vertice 3
            y propiedades comunes de objetos            
    """

    def __init__(self, params):
        super(Triangle, self).__init__(params)

    def get_color(self):
        return self.param("texture", "pigment", "rgb")



    def intersection(self, ray):
        v0 = self.param("v0")
        v1 = self.param("v1")
        v2 = self.param("v2")

         # Vector unitario a la superficie del plano
         
        v0v1 = v1-v0
        v0v2 = v2-v0
        
        n = (v0v1 @ v0v2) * -1

        # Rayo paralelo o no al plano

        nraydir = n * ray.dir
        if abs(nraydir) < epsilon :
            return []               # they are parallel so they don't intersect !

        d = n * v0
        t = (n * ray.loc+d) / nraydir
        
        if t < 0 :
            return []               # the triangle is behind 

        p = ray.loc +  ray.dir * t

        edge0 = v1 - v0
        vp0 = p -v0
        c1 = (edge0 @ vp0)*n
        
        
        edge1 = v2 - v1
        vp1 = p - v1
        c2 = (edge1 @ vp1)*n
        
        
        edge2 = v0 - v2
        vp2 = p - v2
        c3= (edge2 @ vp2)*n
           
           
        if c1 < 0 and c2 < 0 and c3 < 0 :       # P is on the right side
            return [Hit(t, n, self)]
        else :
            return []       

def test_camera():
    pars = [['orthographic', None],
            ['up', VEC3(0.0, 1.0, 0.0)],
            ['look_at', VEC3(0.0, 0.0, 0.0)],
            ['angle', 60.0],
            ['location', VEC3(5.0, 0.0, 0.0)]]
    cam = Camera(pars)
    print(cam)


def test_camera_rays():
    pars = [['orthographic', None],
            ['up', VEC3(0.0, 1.0, 0.0)],
            ['look_at', VEC3(0.0, 0.0, 0.0)],
            ['angle', 60.0],
            ['location', VEC3(5.0, 0.0, 0.0)]]
    cam = Camera(pars)
    ray_gen = cam.ray_generator(32, 24)
    x0 = []; y0 = []
    for ray, x, y in ray_gen:
        x0.append(ray.dir.x)
        y0.append(ray.dir.y)
    plt.plot(x0, y0, '*')
    plt.grid()
    plt.show()



def test_light():
    pars = [('location', VEC3(1, 2, 3)),
            ('rgb', RGB(0.1, 0.3, 0.5)),
            ('parallel', None)]
    light = Light(pars)
    print(light)


def test_sphere():
    pars = [['location', VEC3(1, 2, 3)], ['radius', 1.3]]
    sphere = Sphere(pars)
    print(sphere)


def test_sphere_hits():
    sphere_pars = [['location', VEC3(0, -1, 3)], ['radius', 1]]
    sphere = Sphere(sphere_pars)
    for raydir in (VEC3(0, 0.2, 1),        # Justo arriba de la esfera
                   VEC3(0, 0, 1),          # Tangencial
                   VEC3(0, -0.2, 1)):      # Impacta a la esfera
        ray = Ray(VEC3(0, 0, 0), raydir.normalized())
        print("Ray: {}".format(ray))
        for hit in sphere.intersection(ray):
            print("  {}".format(ray.at(hit.impact)))


def test_plane():
    pars = [('normal', VEC3(3, 2, 1)), ('distance', -2)]
    plane = Plane(pars)
    print(plane)


def test_triangle():
    pars = [('v0', VEC3(3, 2, 1)), ('v1', VEC3(3, 2, 1)), ('v2', VEC3(3, 2, 1))]
    triangle = Triangle(pars)
    print(triangle)


def main(args):
    # ~ test_camera()
    # ~ test_camera_rays()
    # ~ test_light()
    test_sphere()
    # ~ test_sphere_hits()
    # ~ test_plane()
    test_triangle()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

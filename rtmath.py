#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  rtmath.py
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


from math import sqrt

epsilon = 1e-10

"""
 ____   ____ ____
|  _ \ / ___| __ )
| |_) | |  _|  _ \
|  _ <| |_| | |_) |
|_| \_\\____|____/

"""

class RGB:
    """ Almacena los componentes de colores en formato RGB. Cada
        componente tiene  rango de 0 a 1.
    """

    def __init__(self, r, g = 0.0, b = 0.0):
        """ Constructor recibe los colores en formato:
            rgb         RGB     de otra instancia de RGB
            #RRGGBB     str     Un string con x, y, z en hex
            r, g, b     float   los componentes
        """
        if isinstance(r, RGB):
            self.r, self.g, self.b = r.r, r.g, r.b

        elif isinstance(r, str):
            assert len(r) == 7
            assert(r[0] == "#")
            self.r = int(r[1:3], 16)/255
            self.g = int(r[3:5], 16)/255
            self.b = int(r[5:7], 16)/255

        else:
            self.r, self.g, self.b = r, g, b


    def __str__(self):
        return "RGB({}, {}, {})".format(self.r, self.g, self.b)


    def __repr__(self):
        return "RGB({}, {}, {})".format(self.r, self.g, self.b)


    def __eq__(self, val_rgb2):
        """ Compara los componentes r, g, b
        """
        return ((self.r == val_rgb2.r) and
                (self.g == val_rgb2.g) and
                (self.b == val_rgb2.b))


    def __add__(self, val_rgb2):
        """ Suma, componente por componente
        """
        return RGB(self.r + val_rgb2.r,
                   self.g + val_rgb2.g,
                   self.b + val_rgb2.b)


    def __mul__(self, factor):
        """ Multipla los 3 componentes por un factor (=escalea)
        """
        if isinstance(factor, RGB):
            return RGB(self.r * factor.r,
                       self.g * factor.g,
                       self.b * factor.b)
        else:
            return RGB(self.r * factor,
                       self.g * factor,
                       self.b * factor)


    def as_tuple(self):
        return int(self.r*255), int(self.g*255), int(self.b*255)


    def limit(self):
        """ Limita los componentes al rango de 0..1
        """
        self.r = min(self.r, 1.0)
        self.g = min(self.g, 1.0)
        self.b = min(self.b, 1.0)


class RGB_colors:
    Black   = RGB(0, 0, 0)

    Red     = RGB(1, 0, 0)
    Green   = RGB(0, 1, 0)
    Blue    = RGB(0, 0, 1)

    White   = RGB(1, 1, 1)
    Yellow  = RGB(1, 1, 0)
    Cyan    = RGB(0, 1, 1)
    Magenta = RGB(1, 0, 1)
    Orange  = RGB(1, 0.5, 0)
    Brown   = RGB(0.5, 0, 0)
    Purple  = RGB(0.5, 0, 1)

    Gray10  = RGB(0.1, 0.1, 0.1)
    Gray20  = RGB(0.2, 0.2, 0.2)
    Gray30  = RGB(0.3, 0.3, 0.3)
    Gray40  = RGB(0.4, 0.4, 0.4)
    Gray50  = RGB(0.5, 0.5, 0.5)
    Gray60  = RGB(0.6, 0.6, 0.6)
    Gray70  = RGB(0.7, 0.7, 0.7)
    Gray80  = RGB(0.8, 0.8, 0.8)
    Gray90  = RGB(0.9, 0.9, 0.9)
    Gray = Gray50


"""
__     _______ ____ _____
\ \   / / ____/ ___|___ /
 \ \ / /|  _|| |     |_ \
  \ V / | |__| |___ ___) |
   \_/  |_____\____|____/

"""

class VEC3:
    """ Clase almacena y define operaciones con vectores de 3 componentes
        x, y, z : Compoentes del vector
    """
    def __init__(self, x, y = 0, z = 0):
        """ Constructor recibe datos de las siguiente formas
            x, y, z:    float   Componentes separados
            x           tuple   Componentes x, y, z en forma de tupla
            x           VEC3    Un VEC3
            x           str     Si x es 'x', 'y', 'z', genera un vector
                                paralelo al eje correspondiente
        """
        if isinstance(x, tuple):
            self.x, self.y, self.z = x

        elif isinstance(x, VEC3):
            self.x, self.y, self.z = x.x, x.y, x.z

        elif isinstance(x, str):
            assert x in "xyz"
            if   x == "x": self.x, self.y, self.z = 1, 0, 0
            elif x == "y": self.x, self.y, self.z = 0, 1, 0
            elif x == "z": self.x, self.y, self.z = 0, 0, 1

        else:
            self.x, self.y, self.z = x, y, z


    def __str__(self):
        return "VEC3({}, {}, {})".format(self.x, self.y, self.z)


    def __repr__(self):
        return "VEC3({}, {}, {})".format(self.x, self.y, self.z)


    def __abs__(self):
        """ Valor absoluto (= largo del vector)
        """
        return sqrt(self.x**2 + self.y**2 + self.z**2)


    def __add__(self, v2):
        """ Suma
        """
        return VEC3(self.x + v2.x, self.y + v2.y, self.z + v2.z)


    def __sub__(self, v2):
        """ Resta
        """
        return VEC3(self.x - v2.x, self.y - v2.y, self.z - v2.z)


    def __mul__(self, v2):
        """ Producto punto (escalar)
        """
        if isinstance(v2, VEC3):
            return self.x*v2.x + self.y*v2.y + self.z*v2.z
        else:
            return VEC3(self.x*v2, self.y*v2, self.z*v2)


    def __matmul__(self, v3):
        """ Producto cruz (vectorial)
        """
        return VEC3(self.y * v3.z - self.z * v3.y,
                    self.z * v3.x - self.x * v3.z,
                    self.x * v3.y - self.y * v3.x)


    def normalize(self):
        d = abs(self)
        self.x /= d
        self.y /= d
        self.z /= d


    def normalized(self):
        d = abs(self)
        v = VEC3(self.x / d,
                 self.y / d,
                 self.z / d)
        return v


    def to_tuple(self):
        return (self.x, self.y, self.z)


"""
 ____
|  _ \ __ _ _   _
| |_) / _` | | | |
|  _ < (_| | |_| |
|_| \_\__,_|\__, |
            |___/
"""

class Ray:
    """ Clase para almacenar y procesar rayos.
        loc     Origen del rayo
        dir     Dirección del ray
    """
    def __init__(self, loc, dir):
        self.loc, self.dir = loc, dir


    def __str__(self):
        return "ray[loc={}, dir={}]".format(self.loc, self.dir)


    def at(self, t):
        """ at      Ubicación a una distancia t
        """
        return self.loc + self.dir * t

"""
 _   _ _ _
| | | (_) |_
| |_| | | __|
|  _  | | |_
|_| |_|_|\__|

"""

class Hit:
    def __init__(self, impact, normal, thing):
        self.impact = impact
        self.normal = normal
        self.thing = thing


    def __str__(self):
        return "hit(impact: {}, normal: {}, thing: {})".format(
                self.impact, self.normal, self.thing)



def test_rgb():
    rgb = RGB(0.1, 0.5, 1)
    print(rgb)
    rgb2 = RGB(rgb)
    print(rgb2)
    rgb3 = RGB("#34A53f")
    print(rgb3)
    print(rgb == rgb2)

    rgb = RGB(0.1, 0.5, 1)
    rgb += rgb
    print(rgb)
    rgb.limit()
    print(rgb)


def test_vec3():
    v3 = VEC3(1, 2, 3)
    print(v3)
    v3a = VEC3(v3)
    print(v3, v3a)

    print("Abs = ", abs(v3))
    v3.normalize()
    print("Abs = {}    {}".format(abs(v3), v3))

    v3 = VEC3((1, 2, 3))
    print(v3 + VEC3(4,3,2))
    print(v3.to_tuple())
    print(v3, v3*1.5)


def test_ray():
    ray = Ray(VEC3(1, 2, 3), VEC3(3, 4, 5))
    print(ray)


def main(args):
    # ~ test_rgb()
    test_vec3()
    # ~ test_ray()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

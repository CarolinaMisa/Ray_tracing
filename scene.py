#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  scene.py
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

from rtmath import Ray, epsilon
from things import Sphere, Plane, Triangle, Camera, Light
import pdb

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf, GLib, Gtk


def pixbuf2image(pix):
    """ Convert gdkpixbuf to PIL image
    """
    data = pix.get_pixels()
    w = pix.props.width
    h = pix.props.height
    stride = pix.props.rowstride
    mode = "RGB"
    if pix.props.has_alpha == True:
        mode = "RGBA"
    im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
    return im


def image2pixbuf(im):
    """ Convert Pillow image to GdkPixbuf
    """
    data = im.tobytes()
    w, h = im.size
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
            False, 8, w, h, w * 3)
    return pix



class Scene():
    def __init__(self):
        self.clear()


    def clear(self):
        self.els = {
                    "directives": [],
                    "cameras": [],
                    "lights": [],
                    "objects": []}

    def classify(self, parsed):
        things = {"sphere": Sphere, "plane": Plane, "triangle": Triangle}
        print(parsed)
        for key, value in parsed:
            if   key == "camera":
                self.els["cameras"].append(Camera(value))

            elif key == "light_source":
                self.els["lights"].append(Light(value))

            elif key in things:
                self.els["objects"].append(things[key](value))

            elif key[0] == "#":
                self.els["directives"] += key, value

            else:
                print("Tipo de elemento no conocido ({})".format(key))


    def things(self):
        for obj in self.els["objects"]:
            yield obj


    def lights(self):
        for light in self.els["objects"]:
            yield light


    def dump(self):
        for cat in ("directives", "cameras", "lights", "objects"):
            print(cat)
            for el in self.els[cat]:
                print("    {}".format(el))


    def find_nearest_thing_hit(self, ray):
        hits = []
        for obj in self.els["objects"]:
            hits += obj.intersection(ray)

        if hits == []:
            return None

        nearest = None
        for hit in hits:
            if hit.impact > 0:
                if (nearest is None) or (hit.impact < nearest.impact):
                    nearest = hit

        return nearest


    def tracer(self, toplevel):
        """ para todos los rayos
                para todos los objetos
                    para el impacto mas cercano
                        - luz ambiente (color)
                        para cada fuente de luz
                            para cada objeto ver si permite la luz
                                si llega luz, determinar el ángulo de la luz
                                    determinamos intensidad la luz -> difusa
                                    determinar luz especular
        """
        self.toplevel = toplevel
        w = toplevel.config.conf["image"]["width"]
        h = toplevel.config.conf["image"]["height"]

        if len(self.els["cameras"]) != 1:
            return "Tiene que existir exactamente una sola cámara. Hay {}.".format(
                        len(self.els["cameras"]))

        if len(self.els["objects"]) == 0:
            return "No hay objetos en la escena"

        self.cam = self.els["cameras"][0]
        ray_gen = self.cam.ray_generator(w, h)
        GLib.timeout_add(500, self.on_timeout)
        self.timer_runs = True

        for ray, x0, y0 in ray_gen:
            Gtk.main_iteration_do(False)
            nearest_hit = self.find_nearest_thing_hit(ray)
            if nearest_hit is None:   # No hay impactos: No ejecutamos el resto
                continue

            nearest_color = nearest_hit.thing.get_color()
            pixel_color = nearest_color * toplevel.config.conf["scene"]["ambient"]

            for light in self.els["lights"]:
                light_loc = light.param("location")
                light_color = light.param("rgb")

                incident = (ray.at(nearest_hit.impact) - light_loc).normalized()
                light_ray = Ray(light_loc, incident)

                nearest_light_hit = self.find_nearest_thing_hit(light_ray)

                if nearest_light_hit is None:       # imposible
                    continue

                light_to_hit = abs(light_loc - ray.at(nearest_hit.impact))
                if (nearest_light_hit.impact - light_to_hit) > -epsilon:
                    cos_ang = -(nearest_light_hit.normal * incident)
                    diffuse = nearest_color * light_color
                    pixel_color += diffuse * cos_ang

            self.cam.set_pixel(x0, h - y0 - 1, pixel_color)

        self.timer_runs = False


    def on_timeout(self):
        self.toplevel.render.set_from_pixbuf(image2pixbuf(self.cam.image))
        return self.timer_runs


def main(args):

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

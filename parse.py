#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  parse.py
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

import pyparsing as pp
import numpy as np
import pdb
from collections import OrderedDict
from numbers import Number
from rtmath import VEC3, RGB
from things import Camera, Light, Sphere, Plane
from scene import Scene


class Pov_parser:
    def __init__(self):
        pass


    def from_string(self, source):
        parser = self.make_parser()
        print(parser.parseString(source))


    def to_vector(self, tkn):
        AXIS = {"x": np.array([1, 0, 0]),
                "y": np.array([0, 1, 0]),
                "z": np.array([0, 0, 1])}
        return list(AXIS[tkn[0]] * float(tkn[1]))


    def make_parser(self, which = "parser"):
        open_par = pp.Literal("{").suppress()
        close_par = pp.Literal("}").suppress()

        unsigned = pp.Word(pp.nums)
        signed   = pp.Combine(pp.Optional(pp.oneOf("- +")) + unsigned)

        floatn = pp.Combine(
                    signed +
                    pp.Optional(pp.Literal(".") + unsigned) +
                    pp.Optional(pp.oneOf("e E") + signed))
        floatn = floatn.setParseAction(lambda tkn: float(tkn[0]))

        vector = (
                    (pp.Literal("<").suppress() +
                        floatn + pp.Literal(",").suppress() +
                        floatn + pp.Literal(",").suppress() +
                        floatn + pp.Literal(">").suppress()).setParseAction(
                                            lambda t: VEC3(t[0], t[1], t[2])) |
                     pp.Literal("x").setParseAction(lambda t: VEC3(1.0, 0.0, 0.0)) |
                     pp.Literal("y").setParseAction(lambda t: VEC3(0.0, 1.0, 0.0)) |
                     pp.Literal("z").setParseAction(lambda t: VEC3(0.0, 0.0, 1.0)))

        color_vector = (
                    (pp.Literal("<").suppress() +
                        floatn + pp.Literal(",").suppress() +
                        floatn + pp.Literal(",").suppress() +
                        floatn + pp.Literal(">").suppress()).setParseAction(
                                            lambda t: RGB(t[0], t[1], t[2])))

        color = (pp.Keyword("rgb") + color_vector).setParseAction(lambda t: ["rgb", t[1]])

        pigment_item = color

        pigment_items = pp.Group(pp.OneOrMore(pigment_item))

        pigment = (
                    pp.Keyword("pigment").suppress() +
                    open_par +
                        pigment_items +
                    close_par).setParseAction(lambda t: ["pigment", t[0]])

        reflection = pp.Group(pp.Keyword('reflection') + floatn)("reflection")

        finish_item = reflection

        finish_items = pp.Group(pp.OneOrMore(finish_item))

        finish = (
                    pp.Keyword("finish").suppress() +
                    open_par +
                        finish_items +
                    close_par).setParseAction(lambda t: ["finish", t[0]])

        
        texture_item = pp.Group(pigment | finish)

        texture_items = pp.Group(
                    pp.OneOrMore(texture_item))

        texture = (pp.Keyword("texture") +
                    open_par +
                        texture_items +
                    close_par).setParseAction(lambda t: ["texture", t[1]])

        object_modifier = pp.Group(texture)
        object_modifiers = pp.ZeroOrMore(object_modifier)

        cam_types  = pp.oneOf("orthographic").setParseAction(lambda t: [[t[0], None]])
        cam_loc    = (pp.Keyword("location") + vector).setParseAction(lambda t: [["location", t[1]]])
        cam_angle  = (pp.Keyword("angle") + floatn).setParseAction(lambda t: [["angle", t[1]]])
        cam_lookat = (pp.Keyword("look_at") + vector).setParseAction(lambda t: [["look_at", t[1]]])
        cam_up     = (pp.Keyword("up") + vector).setParseAction(lambda t: [["up", t[1]]])
        cam_items = pp.Group(
                     cam_loc & cam_angle & cam_lookat & pp.Optional(cam_types) &
                     pp.Optional(cam_up))

        camera = pp.Group(
                    pp.Keyword("camera") +
                    pp.Literal("{").suppress() +
                    cam_items +
                    pp.Literal("}").suppress())

        light_modifiers = pp.Optional(pp.Keyword("parallel").setParseAction(lambda t: [[t[0], None]]))

        light = pp.Group(
                    pp.Keyword("light_source") +
                    open_par +
                    pp.Group(
                        vector.copy().setParseAction(lambda t: [["location", t[0]]]) +
                        pp.Literal(",").suppress() +
                        color.setParseAction(lambda t: [["rgb", t[1]]]) +
                        light_modifiers) +
                    close_par)

        sphere = pp.Group(pp.Keyword("sphere") +
                    open_par +
                    pp.Group(
                        vector.copy().setParseAction(lambda t: [["location", t[0]]]) +
                        pp.Literal(",").suppress() +
                        floatn("radius").copy().setParseAction(lambda t: [["radius", float(t[0])]]) +
                        object_modifiers) +
                    close_par)

        plane = pp.Group(pp.Keyword("plane") +
                    open_par +
                    pp.Group(
                        vector.copy().setParseAction(lambda t: [["normal", t[0]]]) +
                        pp.Literal(",").suppress() +
                        floatn("distance").copy().setParseAction(lambda t: [["distance", float(t[0])]]) +
                        object_modifiers) +
                    close_par)

        triangle = pp.Group(pp.Keyword("triangle") + 
                   open_par +
                   pp.Group(
                        vector.copy().setParseAction(lambda t: [["v0", t[0]]]) +
                        pp.Literal(",").suppress() +
                        vector.copy().setParseAction(lambda t: [["v1", t[0]]]) +
                        pp.Literal(",").suppress() +
                        vector.copy().setParseAction(lambda t: [["v2", t[0]]]) +
                        object_modifiers) + 
                   close_par)


        graph_els = camera | light | sphere | plane | triangle

        parser = pp.OneOrMore(graph_els)
        return eval(which)



def test_subexpression(element):
    TESTS = {"floatn":      ("1", "1.3", "-1.3", "1e5", "1e-5", "1.33e5"),
             "vector":      ("<1.3, -5, +1.5>", "y, 5.6"),
             "plane":       ('plane {  y, -4.5 }', ),
             "camera":      ('camera { location <0, 1, 2> up <0, 1, 0> '
                                'look_at <0, 0, 0> angle 60}', ),
             "texture":     ('texture { pigment { rgb <1, 1, 1> }}', ),
             "color":       ('rgb <1, 1, 1> ', ),
             "pigment":     ('pigment { rgb <1, 1, 1> }', ),
             'reflection':  ('reflection 0.7', ),
             "finish":      ('finish { reflection 0.6}', ),
             "rotate":      ('rotate <20, 40, 20>', ),
             "triangle":    ( 'triangle {<1, 0, 0>, <0, 1, 0>, <0, 0, 1>}', )
            }

    strings = TESTS[element]
    pov = Pov_parser()
    parser = pov.make_parser(element)
    for s in strings:
        print(parser.parseString(s))


def test_parser():
    pov = Pov_parser()
    parser = pov.make_parser()
    script = ""
    for add in ('#include "dsfdf"\n',
                'camera { up <0, 1, 0> look_at <0, 0, 0> location <-5, 0, 0>}',
                'light_source { <10, 10, -20>, rgb <1, 1, 0> }',
                'sphere { <0, 0, 0>, 1 }',
                'plane {  y, -4.5 }'):
        print("---->", add)
        script += add
        parser.parseString(script)


def test_classifier():
    script = (
              'camera { orthographic up <0, 1, 0> look_at <0, 0, 0> angle 60 location <-5, 0, 0>}'
              'light_source { <10, 10, -20>, rgb <1, 1, 0>  parallel}'
              'sphere { <0, 0, 0>, 1 texture { pigment { rgb <1, 1, 1> }} }'
              'plane { y, -4.5  }'
              'triangle {<1, 0, 0>, <0, 1, 0>, <0, 0, 1> pigment {rgb <0, 1, 1>}}')
 
    pov = Pov_parser()
    parser = pov.make_parser()
    temp = parser.parseString(script).asList()

    scene = Scene()
    scene.classify(temp)
    scene.dump()


def main(args):
    # ~ test_subexpression("floatn")
    # ~ test_subexpression("vector")
    # ~ test_subexpression("plane")
    # ~ test_parser()
   # test_subexpression("camera")
    # ~ test_subexpression("color")
    # ~ test_subexpression("pigment")
    # ~ test_subexpression(("texture")
    # ~ test_subexpression("reflection")
    # ~ test_subexpression("finish")
    test_subexpression("triangle")
    #test_classifier()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

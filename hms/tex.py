# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "\\textcolor{{deepgold}}{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{\\rotatebox{{90}}{{{}}}}}".format(txt)

def link(txt, dest):
    return txt

def num(n):
    return n

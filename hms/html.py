# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "<span>{}</span>".format(txt)

def superscript(txt):
    return "<sup>{}</sup>".format(txt)

def num(n):
    return num2cn(num, traditional=True)

# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "<span>{}</span>".format(txt)

def superscript(txt):
    return "<sup>{}</sup>".format(txt)

def linl(txt, dest):
    return "<a href=\"https://www.lucum.net/index.php?ident={}\">{}</a>".format(dest, txt)

def num(n):
    return num2cn(num, traditional=True)

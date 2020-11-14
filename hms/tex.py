# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "\\textbf{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{{}}}".format(txt)

def link(txt, dest):
    return txt

def num(n):
    return pycnnum.num2cn(num, traditional=True)

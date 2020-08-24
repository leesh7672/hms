# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "\\textbf{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{{}}}".format(txt)

def num(n):
    return num2cn(num, traditional=True)

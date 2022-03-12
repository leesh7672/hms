# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "\\textcolor{{gold}}{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{{}}}".format(txt)

def link(txt, dest):
    return txt

def num(n):
    return n

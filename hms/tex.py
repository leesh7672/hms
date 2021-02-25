# -*- coding: utf-8 -*-

import pycnnum

def bold(txt):
    return "\\textcolor{{blue}}{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{{}}}".format(txt)

def link(txt, dest):
    return txt

def num(n):
    return n

def ref(ident, page):
    return "\\autocite{}{{{}}}".format(page, ident)

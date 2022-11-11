# -*- coding: utf-8 -*-

def cancel(txt):
    return "\\cancel{{{}}}".format(txt)

def bold(txt):
    return "\\textcolor{{deepgold}}{{{}}}".format(txt)

def superscript(txt):
    return "\\textsuperscript{{\\rotatebox{{90}}{{{}}}}}".format(txt)

def link(txt, dest):
    return txt

def num(n):
    return "\\zhnumber{{{}}}".format(n)

# -*- coding: utf-8 -*-
import os
import uuid
from operator import itemgetter, methodcaller, mul

from cihai.core import Cihai
from lxml import etree

c = Cihai()

import hms.tex as tex

parser = etree.XMLParser(remove_blank_text=False)

def generateIdent():
    return str(uuid.uuid4())

categories = {'comp':"成字", 'infl':"助字", 'adv':"副字", 'v': "外動字", 'verb': "動字", 'adj': "形字", 'coverb': "介字", 'det': "指字", 'noun':"名字", 'cl': "量字", 'num':"數字"}

def xp(e, default_mode="auto"):
    category = e.attrib['category']
    children = []
    if "mode" in e.attrib:
        mode = e.attrib["mode"]
    else:
        mode = default_mode
    if mode == "roof":
        text = textify(e)
        if text == "":
            text = "…"
        formula = "[{} [{}, roof]]".format(categories[category] + "組", text)
    elif mode == "auto" or mode=="autoroof":
        for child in e:
            if child.tag == "xp":
                children += [xp(child, "roof")]
            elif child.tag == "xbar":
                grandchildren = []
                xbar_text = ""
                xbar_formula = f"[{categories[category]}片組 "
                for grandchild in child:
                    if grandchild.tag == "xp":
                        grandchildren += [xp(grandchild, "roof")]
                    elif grandchild.tag == "x":
                        spell = textify(grandchild)
                        grandchildren += [(category, spell, f"[{categories[category]} [{spell}]]")]
                for grandchild in grandchildren:
                    (_, x_spell, x_formula) = grandchild
                    xbar_text += x_spell
                    xbar_formula += " " + x_formula
                children += [(category, xbar_text, xbar_formula+"]")]
        text = ""
        formula =  f"[{categories[category]}組"
        for child in children:
            (_, child_text, child_formula) = child
            text += child_text
            formula += child_formula
        formula += "]"
        if text == "":
            text  = "…"
            mode = "autoroof"
        if mode == "autoroof":
            formula = "[{} [{}, roof]]".format(categories[category] + "組", text)
    return category, text, formula
def fullpunct(half: str):
    return half.replace('\n', '').replace('\t', '').replace(' ', '').replace('.', '。').replace(',', '、').replace('(', '（').replace(')', '）').replace(':', '：')
def textify(e):
    if e.text is not None:
        total = fullpunct(e.text)
    else:
        total = ""
    for child in e:
        if child.tag == 'samp':
            if 'source' in child.attrib:
                source = child.attrib['source']
            else:
                source = "例"
            total += "\\linebreak{{}}{{{1}曰『{2}』}}".format(source, textify(child))
        elif child.tag == 'xp':
            total += "\\linebreak\\begin{{forest}}{}\\end{{forest}}".format(xp(child)[2])
        elif child.tag == 'quote':
            temp = textify(child)
            level = 1
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '『{}』”'.format(temp)
            elif level >= 2:
                total += '「{}」'.format(temp)
        elif child.tag == 'bold':
            total +="\\textbf{{{}}}".format(textify(child))
        elif child.tag == 'cancel':
            total +="\\cancel{{{}}}".format(textify(child))
        elif child.tag == 'zero':
            total += "∅"
        elif child.tag == 'ref':
            ident = child.attrib['identifier']
            (tr, f) = search(ident)
            root = tr.getroot()
            num = 1
            notation = ''
            if 'index' in root.attrib.keys():
                num = int(root.attrib['index'])
            if 'spell' in root.attrib.keys():
                spell = root.attrib['spell']
            notation = "\\textbf{{{}}}\\textsuperscript{{{}}}".format(spell, num)
            total += notation
        if child.tail is not None:
            total += fullpunct(child.tail)
    return total.strip()

def scandef(e, spell, ident, coder=tex):
    synonyms = []
    antonyms = []
    samples = []
    explanation = ''
    if not('index' in e.attrib.keys()):
        num = 1
    else:
        num = e.attrib['index']
    if 'category' in e.attrib.keys():
        category = categories[e.attrib['category']]
        sp = '・'
    else:
        category = ''
        sp = ''
    counter = 0
    explanation=textify(e)
    return (num, category.replace("PRIM", ''), synonyms, antonyms, samples, explanation)
def search(ident):
    for (path, dir, files) in os.walk('entries'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            if os.path.isfile(p):
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    tree = etree.parse(p, parser)
                    root = tree.getroot()
                    if  'identifier' in root.attrib:
                        if root.attrib['identifier'] == ident:
                            if root.tag == 'entry':
                                return (tree, p)
    return None

def updatexml(path):
    print(path)
    tree = etree.parse(path, parser)
    root = tree.getroot()
    if not('identifier' in root.attrib.keys()):
        root.set('identifier', '{}'.format(generateIdent()))
        tree.write(path)
    if not('index' in root.attrib.keys()):
        root.set('index', '1')
        num = '1'
    else:
        num = root.attrib['index']
    for child in root:
        if child.tag == 'usage' and not ('index' in child.attrib.keys()):
            child.set('index', '1')
    ident = root.attrib['identifier']
    etree.ElementTree(tree.getroot()).write(path, pretty_print=True, encoding='Big5')
def scanxml(tree):
    root = tree.getroot()
    num = root.attrib['index']
    ident = root.attrib['identifier']
    notation = []
    spell = ''
    cites = ''
    if root.tag == 'entry':
        spell = root.attrib["spell"]
        definitions = [scandef(root, spell, ident)]
    return (root, num, spell, ident, notation, definitions, cites)
def _spell(x):
    global c
    skip = False
    respell = ''
    for ch in x:
        if not skip:
            respell  = respell + x
    total = []
    for ch in respell:
        kangxi =  c.unihan.lookup_char(ch).first().kRSKangXi.split('.')
        total += [int(kangxi[0]), int(kangxi[1])]
    return total + [0, 0]
def update():
    for (path, dir, files) in os.walk('./'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            ext = os.path.splitext(filename)[-1]
            if ext == '.xml':
                updatexml(p)
class entry:
    def __init__(self, values):
        self.values =values
    def index_spell(self):
        return _spell(self.values)
def collect_entries(code=tex):
        results = []
        for (path, dir, files) in os.walk('entries'):
            for filename in files:
                p = '{}/{}'.format(path, filename)
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    print(p)
                    results += [scanxml(etree.parse(p))]
        return sorted(results, key=lambda x: _spell(x[2]) + [x[1]])

def build():
    results = collect_entries(tex)
    txt = ''
    for result in results:
        (root, num, spell, ident, alternative_spells, definitions, cites) = result
        spells = ''
        definition_txt = ''
        for d in sorted(definitions, key=itemgetter(0)):
            (numx, category_txt, synonyms, antonyms, samples, explanation) = d
            synonym_txt = ''
            antonym_txt = ''
            sample_txt = ''

            for synonym in synonyms:
                synonym_txt += "\\syn{{{}}}{{{}}}".format(synonym[0], synonym[1])

            for antonym in antonyms:
                antonym_txt += "\\ant{{{}}}{{{}}}".format(antonym[0], antonym[1])

            for sample in samples:
                sample_txt += sample

            definition_txt += "\\explain{{{}}}{{{}{}{}{}}}".format(category_txt, explanation, synonym_txt, antonym_txt, sample_txt)
        txt+= "\\entry{{{}}}{{{}}}{{{}{}{}}}{{{}}}".format(spell.replace('（', "").replace('）', ''), num, spells, definition_txt, cites, '')
    return txt
def initialize():
    global c
    if not c.unihan.is_bootstrapped:
        c.unihan.bootstrap()
initialize()

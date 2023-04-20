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

categories = {'C': "成", 'I': "助", 'Adv': "副", 'V': "述", 'v': "謂", 'P': "介", 'D': "指", 'N': "名", 'Cl': "量", 'Num': "數", 'Co': "連"}

def scancategory(expr):
    if expr[0] == "*":
        strength = "遷移"
        expr = expr[1:]
    else:
        strength = ""
    return (strength, "{}詞".format(categories[expr]))

def fullpunct(half: str):
    return half.replace('\n', '').replace('\t', '').replace(' ', '').replace('.', '。').replace(',', '、').replace('(', '（').replace(')', '）').replace(':', '：')
def textify(e, en):
    if e.text is not None:
        total = fullpunct(e.text)
    else:
        total = ""
    for child in e:
        if child.tag == 'sample':
            total += "例曰：「{}」。".format(textify(child, en))
        elif child.tag == 'bracket':
            total += "〔{}〕".format(textify(child, en))
        elif child.tag == 'self':
            total += en.attr['spell']
        elif child.tag == 'quote':
            temp = textify(child, en)
            level = 1
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '「{}」'.format(temp)
            elif level >= 2:
                total += '『{}』'.format(temp)
        elif child.tag == 'bold':
            total +="\\textbf{{{}}}".format(textify(child, en))
        elif child.tag == 'cancel':
            total +="\\cancel{{{}}}".format(textify(child, en))
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
        (mstrength, mcategory) = scancategory(e.attrib['category'])
        category = "〔{}{}詞〕".format(mstrength, mcategory)
    else:
        category =""
    if 'complement' in e.attrib.keys():
        if 'argument' in e.attrib.keys():
            (mstrength, mcategory) = scancategory(e.attrib['argument'])
            if e.attrib['category'] == "T":
                opt = "俱"
            else:
                opt = ""
            argument = "，{}在{}組{}下".format(opt, mcategory, mstrength)
        else:
            argument = ""
        (mstrength, mcategory) = scancategory(e.attrib['complement'])
        if e.attrib['category'] == "T":
            formula = "（應{}{}組下{}）".format(mstrength, mcategory, argument)
        else:
            formula = "（應{}{}組上{}）".format(mstrength, mcategory, argument)
    else:
        formula = ""
    explanation=textify(e)
    return (num, category+formula, synonyms, antonyms, samples, explanation)
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
    etree.ElementTree(tree.getroot()).write(path, pretty_print=True, encoding='utf-8')
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

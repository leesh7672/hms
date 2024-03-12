# -*- coding: utf-8 -*-
import os
import uuid
from operator import itemgetter, methodcaller, mul

from cihai.core import Cihai
from lxml import etree

c = Cihai()

parser = etree.XMLParser(remove_blank_text=False)

def generateIdent():
    return str(uuid.uuid4())

categories = {
    'Adv':"狀詞",
    'A':"性詞",
    'N':"名詞",
    'Num':"數詞",
    'Cl':"量詞",
    'D':"指詞",
    'P':"介詞",
    'V':"動詞",
    'T':"候詞",
    'C':"氣詞",
    'AdvP':"狀詞詞組",
    'AP':"性詞詞組",
    'NP':"名詞詞組",
    'NumP':"數詞詞組",
    'ClP':"量詞詞組",
    'DP':"指詞詞組",
    'PP':"介詞詞組",
    'VP':"動詞詞組",
    'TP':"候詞詞組",
    'CP':"氣詞詞組",
}

def scancategory(expr):
    return categories[expr]

def scanrule(e, spell):
    if "category" in e.attrib:
        lab= (scancategory(e.attrib["category"]))
    else:
        lab = ""
    r = ""
    plus = False
    for child in e:
        if child.tag == "a":
            if plus:
                r += '＋'
            r += scanrule(child, spell)
            plus = True
        elif child.tag == "h":
            if plus:
                r += '＋'
            r += "\\textcolor{{c3}}{{\\textbf{{{}}}}}".format(spell)
            plus = True
    if plus:
        return "［\\textsubscript{{{}}}{}］".format(lab, r)
    else:
        return lab
def fullpunct(half: str):
    return half.replace('\n', '').replace('\t', '').replace(' ', '').replace('.', '。').replace(',', '、').replace('(', '（').replace(')', '）').replace(':', '：')
def textify(e, en, level = 1):
    if e.text is not None:
        total = fullpunct(e.text)
    else:
        total = ""
    for child in e:
        if child.tag == 'sample':
            total += "例曰『{}』。".format(textify(child, en))
        elif child.tag == 'quote':
            temp = textify(child, en, 2)
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '『{}』'.format(temp)
            elif level >= 2:
                total += '「{}」'.format(temp)
        elif child.tag == 'bold':
            total +="\\textbf{{{}}}".format(textify(child, en))
        elif child.tag == 'cancel':
            total +="\\cancel{{{}}}".format(textify(child, en))
        elif child.tag == 'format':
            total += scanrule(child, en.attrib['spell'])
        elif child.tag == 'zero':
            total += "∅"
        elif child.tag == 'self':
            total += "\\textcolor{{c3}}{{\\textbf{{{}}}}}".format(en.attrib['spell'])
        elif child.tag == 'ref':
            ident = child.attrib['id']
            (tr, f) = search(ident)
            root = tr.getroot()
            num = 1
            notation = ''
            if 'index' in root.attrib.keys():
                num = int(root.attrib['index'])
            if 'spell' in root.attrib.keys():
                spell = root.attrib['spell']
            notation = "\\textcolor{{c3}}{{\\textbf{{{}}}}}\\textsuperscript{{\\Rensuji{{{}}}}}".format(spell, num)
            total += notation
        if child.tail is not None:
            total += fullpunct(child.tail)
    return total.strip()

def scandef(e, spell, ident):
    synonyms = []
    antonyms = []
    samples = []
    explanation = ''
    if not('index' in e.attrib.keys()):
        num = 1
    else:
        num = e.attrib['index']
    if 'category' in e.attrib.keys():
        mcategory = scancategory(e.attrib['category'])
        category = "〔{}〕".format(mcategory)
    else:
        category =""
    explanation=textify(e, e)
    return (num, category, synonyms, antonyms, samples, explanation)
def search(ident):
    for (path, dir, files) in os.walk('entries'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            if os.path.isfile(p):
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    tree = etree.parse(p, parser)
                    root = tree.getroot()
                    if  'id' in root.attrib:
                        if root.attrib['id'] == ident:
                            if root.tag == 'entry':
                                return (tree, p)
    return None

def updatexml(path):
    print(path)
    tree = etree.parse(path, parser)
    root = tree.getroot()
    if not('id' in root.attrib.keys()):
        root.set('id', '{}'.format(generateIdent()))
        tree.write(path)
    if not('index' in root.attrib.keys()):
        root.set('index', '1')
        num = '1'
    else:
        num = root.attrib['index']
    for child in root:
        if child.tag == 'usage' and not ('index' in child.attrib.keys()):
            child.set('index', '1')
    ident = root.attrib['id']
    etree.ElementTree(tree.getroot()).write(path, pretty_print=True, encoding='utf-8')
def scanxml(tree):
    root = tree.getroot()
    num = root.attrib['index']
    ident = root.attrib['id']
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
def collect_entries():
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
    results = collect_entries()
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

# -*- coding: utf-8 -*-
from lxml import etree
import os, uuid
from operator import methodcaller, itemgetter, mul
from cihai.core import Cihai
c = Cihai()

import hms.tex as tex
import hms.html as html

parser = etree.XMLParser(remove_blank_text=False)

def generateIdent():
    return str(uuid.uuid4())

categories = {'comp':"成字", 'infl':"助字", 'adv':"副字", 'verb': "動字", 'prep': "介字", 'det': "指字",'noun':"名字", 'num': "數字"}

def textify(e, spell, ident, coder=tex):
    total = ''
    part = e.text
    beforehand = False
    for child in e:
        if part != None:
            part = part.replace('\n', '').replace('\t', '').replace(' ', '').replace('、', '・').replace('：', '，')
            if part != '':
                total += part
                beforehand = False
        if child.tag == 'sample':
            temp = textify(child, spell, ident, coder)
            total += '例曰，“{}。”'.format(temp)
            beforehand = False
        elif child.tag == 'also':
            temp = textify(child, spell, ident, coder)
            total += '（又曰，‘{}’）'.format(temp)
            beforehand = False
        elif child.tag == 'quote':
            temp = textify(child, spell, ident, coder)
            level = 1
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '“{}”'.format(temp)
            elif level >= 2:
                total += '‘{}’'.format(temp)
            beforehand = False
        elif child.tag == 'b':
            total +=coder.bold(textify(child, spell, ident, coder))
            beforehand = False
        elif child.tag == 'self':
            total +=coder.bold(spell)
            beforehand = False
        elif child.tag == 'ref':
            ident = child.attrib['identifier']
            (tr, f) = search(ident)
            root = tr.getroot()
            num = 1
            notation = ''
            if 'index' in root.attrib.keys():
                num = int(root.attrib['index'])
            for child0 in root:
                if child0.tag == 'notation':
                    notation = coder.bold(child0.text) + coder.superscript(num)
                if child0.tag == 'spell':
                    notation = coder.bold(child0.text) + coder.superscript(num)
            total += notation
            beforehand = False
        part = child.tail
    if part != None:
        if part != '':
            part = part.replace('\n', '').replace('\t', '').replace(' ', '').replace('、', '・').replace('：', '，')
            total += part
            beforehand = True
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
        sp = '，'
    else:
        category = ''
        sp = ''
    counter = 0
    explanation=textify(e, spell, ident)
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
    etree.ElementTree(tree.getroot()).write(path, pretty_print=True, encoding='utf-8')
def scanxml(tree):
    root = tree.getroot()
    num = root.attrib['index']
    ident = root.attrib['identifier']
    notation = []
    definitions= []
    spell = ''
    cites = ''
    if root.tag == 'entry':
        for child in root:
            if child.tag == 'spell':
                notation= child.text.strip()
                spell = "（" + notation + " ）"
            if child.tag == 'notation':
                notation = child.text.strip()
            elif child.tag == 'usage':
                definitions += [scandef(child, notation, ident)]
    return (root, num, spell, ident, notation, definitions, cites)
def _spell(x, num):
    global c
    skip = False
    respell = ''
    for ch in x:
        if ch == '（':
            skip = True
        if not skip:
            respell  = respell + x
        if ch == '）':
            skip = False
    total = [0]
    for ch in respell:
        kangxi =  c.unihan.lookup_char(ch).first().kRSKangXi.split('.')
        total += [int(kangxi[0]), int(kangxi[1])]
    return total + [-1, int(num)]
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
def _work(q, p):
        try:
            q.put(result)
        except Exception as e:
            print('An error has been occurred in {}'.format(p))
def collect_entries(code=tex):
        results = []
        for (path, dir, files) in os.walk('entries'):
            for filename in files:
                p = '{}/{}'.format(path, filename)
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    print(p)
                    results += [scanxml(etree.parse(p))]
        return sorted(results, key=lambda x: _spell(x[4], x[1]))

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

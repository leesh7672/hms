# -*- coding: utf-8 -*-
import xml.etree.ElementTree as elemTree
import os
from operator import methodcaller, itemgetter, mul
from cihai.core import Cihai
c = Cihai()

latest_ident = 0
def generateIdent():
    global latest_ident
    latest_ident += 1
    file = open('counter', 'w')
    file.write('{}'.format(latest_ident))
    file.close()
    return latest_ident

def textify(e, spell, ident):
    total = ''
    part = e.text
    for child in e:
        if part != None:
            part = part.replace('.', '。').replace(',', '，').replace(' ', '').replace('\t', '').replace('\n', '').replace(' ', '')
            total += part
        if child.tag == 'quote':
            temp = textify(child, spell, ident)
            level = 1
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '「{}」'.format(temp)
            elif level >= 2:
                total += '『{}』'.format(temp)
        elif child.tag == 'self':
            total += "\\textbf{{{}}}".format(spell)
        elif child.tag == 'ref':
            ident = int(child.attrib['ident'])
            tr = search(ident)
            root = tr.getroot()
            num = 1
            mspell = ''
            if 'num' in root.attrib.keys():
                num = int(root.attrib['num'])
            for child0 in root:
                if child0.tag == 'main-spell':
                    mspell = child0.text
            total += '\\textbf{{{}}}\\textsuperscript{{\\CJKnumber{{{}}}}}'.format(mspell, num)
        part = child.tail
    if part != None:
        part = part.replace('.', '。').replace(',', '，').replace(' ', '').replace('\t', '').replace('\n', '').replace(' ', '')
        total += part
    return total.strip()
def scandef(e, spell, ident):
    categories = []
    synonyms = []
    antonyms = []
    samples = []
    explanation = ''
    if not('num' in e.attrib.keys()):
        num = 1
    else:
        num = int(e.attrib['num'])
    for child in e:
        if child.tag == 'pronoun':
            categories += ['指字']
        elif child.tag == 'noun':
            categories += ['稱字']
        elif child.tag == 'verb':
            categories += ['述字']
        elif child.tag == 'modifier':
            categories += ['冠字']
        elif child.tag == 'interjection':
            categories += ['歎字']
        elif child.tag == 'connecter':
            categories += ['結字']
        elif child.tag == 'counter':
            categories += ['度字']
        elif child.tag == 'number':
            categories += ['數字']
        elif child.tag == 'adverb':
            categories += ['修字']
        elif child.tag == 'final':
            categories += ['竟字']
        elif child.tag == 'header':
            categories += ['發字']
        elif child.tag == 'misc':
            categories += ['雜字']
        elif child.tag == 'exp':
            explanation = textify(child, spell, ident)
        elif child.tag == 'samp':
            if 'src' in child.attrib.keys():
                source = child.attrib['src']
            else:
                source = ''
            samples += ['《{}》云、「{}」'.format(source, textify(child, spell, ident))]
    return (num, categories, synonyms, antonyms, samples, explanation)
def search(ident):
    for (path, dir, files) in os.walk('./'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            if os.path.isfile(p):
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    tree = elemTree.parse(p)
                    root = tree.getroot()
                    if int(root.attrib['ident']) == ident:
                        if(root.tag == 'entry'):
                            return tree
    return None
def updatexml(path):
    tree = elemTree.parse(path)
    root = tree.getroot()
    if not('ident' in root.attrib.keys()):
        root.set('ident', '{}'.format(generateIdent()))
        tree.write(path)
    if not('num' in root.attrib.keys()):
        root.set('num', '1')
        num = 1
    else:
        num = int(root.attrib['num'])
    ident = int(root.attrib['ident'])
    if root.tag == 'entry':
        for child in root:
            if child.tag == 'def':
                for child0 in child:
                    if child0.tag == 'syn':
                        ident0 = int(child0.attrib['ident'])
                        num0 = int(child0.attrib['num'])
                        ref = search(ident0)
                        for definition in ref.findall('def'):
                            if('num' in definition.attrib.keys()):
                                if(definition.attrib['num']):
                                    need = True
                                    for child1 in definition:
                                        if (child1.tag == 'syn') and (int(child1.attrib['ident']) == ident) and (int(child1.attrib['num'] == int(child.attrib['num']))):
                                            need = False
                                            break
                                    if need:
                                        sub = elemTree.SubElement(definition, 'syn', {'ident':'{}'.format(ident), 'num':'{}'.format(num)})\
                                        definition.append(sub)
                    elif child0.tag == 'ant':
                        ident0 = int(child0.attrib['ident'])
                        num0 = int(child0.attrib['num'])
                        ref = search(ident0)
                        for definition in ref.findall('def'):
                            if('num' in definition.attrib.keys()):
                                if(definition.attrib['num']):
                                    need = True
                                    for child1 in definition:
                                        if (child1.tag == 'ant') and (int(child1.attrib['ident']) == ident) and (child1.ident['num'] == int(child.attrib['num'])):
                                            need = False
                                            break
                                    if need:
                                        sub = elemTree.SubElement(definition, 'ant', {'ident':'{}'.format(ident), 'num':'{}'.format(num)})
                                        definition.append(sub)
    tree.write(path, encoding='utf-8')
def scanxml(tree):
    root = tree.getroot()
    num = int(root.attrib['num'])
    ident = int(root.attrib['ident'])
    alternative_spells = set()
    definitions= []
    if root.tag == 'entry':
        for child in root:
            if child.tag == 'spell':
                alternative_spells += [child.text.strip()]
            elif child.tag == 'main-spell':
                spell = child.text.strip()
            elif child.tag == 'def':
                definitions += [scandef(child, spell, ident)]
    return (root, num, spell, ident, alternative_spells, definitions)
def _spell(x):
    global c
    total = []
    (root, num, spell, ident, alternative_spells, definitions) = x
    for ch in spell:
        total += [c.unihan.lookup_char(ch).first().kRSKangXi]
    return [total, num]
def update():
    for (path, dir, files) in os.walk('./'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            ext = os.path.splitext(filename)[-1]
            if ext == '.xml':
                updatexml(p)
def build():
    class entry:
        def __init__(self, values):
            self.values =values
        def index_spell(self):
            return _spell(self.values)
    update()
    results = []
    for (path, dir, files) in os.walk('./'):
        for filename in files:
            p = '{}/{}'.format(path, filename)
            ext = os.path.splitext(filename)[-1]
            if ext == '.xml':
                result = scanxml(elemTree.parse(p))
                results += [entry(result)]
    tex = ''
    for result in sorted(results, key=methodcaller('index_spell')):
        (root, num, spell, ident, alternative_spells, definitions) = result.values
        spells = ''
        for sp in alternative_spells:
            spells += '\\also{{{}}}'.format(sp)
        definition_txt = ''
        for d in sorted(definitions, key=itemgetter(0)):
            (numx, categories, synonyms, antonyms, samples, explanation) = d
            category_txt = ''
            synonym_txt = ''
            antonym_txt = ''
            sample_txt = ''
            for category in categories:
                category_txt += category

            for synonym in synonyms:
                synonym_txt += synonym

            for antonym in antonyms:
                antonym_txt += antonym

            for sample in samples:
                sample_txt += sample

            definition_txt += "\\explain{{{}}}{{{}{}{}{}}}".format(category_txt, explanation, synonym_txt, antonym_txt, sample_txt)
        tex += "\\entry{{{}}}{{{}}}{{{}{}}}{{{}}}".format(spell, num, spells, definition_txt, '')
    return tex
def initialize():
    global latest_ident
    global c
    file = open('counter')
    latest_ident = int(file.read())
    file.close()
    if not c.unihan.is_bootstrapped:
        c.unihan.bootstrap()
initialize()

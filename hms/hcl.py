# -*- coding: utf-8 -*-
from lxml import etree
import os, uuid
from operator import methodcaller, itemgetter, mul
from cihai.core import Cihai
c = Cihai()

import hms.tex as tex
import hms.html as html

parser = etree.XMLParser(remove_blank_text=True)

def generateIdent():
    return str(uuid.uuid4())

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
        if child.tag == 'samp':
            if 'src' in child.attrib.keys():
                source = child.attrib['src']
            else:
                source = ''
            total += '{}曰，「{}」。'.format(source, textify(child, spell, ident, coder))
            beforehand = False
        if child.tag == 'quote':
            temp = textify(child, spell, ident, coder)
            level = 1
            if 'level' in child.attrib:
                level = int(child.attrib['level'])
            if level == 1:
                total += '「{}」'.format(temp)
            elif level >= 2:
                total += '『{}』'.format(temp)
            beforehand = False
        elif child.tag == 'b':
            total +=coder.bold(textify(child, spell, ident, coder))
            beforehand = False
        elif child.tag == 'self':
            total +=coder.bold(spell)
            beforehand = False
        elif child.tag == 'ref':
            ident = child.attrib['ident']
            (tr, f) = search(ident)
            root = tr.getroot()
            num = 1
            notation = ''
            if 'num' in root.attrib.keys():
                num = int(root.attrib['num'])
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
            part = part.replace('.', '。').replace(',', '、').replace(' ', '').replace('\t', '').replace('\n', '').replace(' ', '')
            total += part
            beforehand = True
    return total.strip()
categories = {'comp':"成詞", 'infl':"助詞", 'adv':"副詞", 'lv': "外動詞", 'acc':"賓詞", 'verb': "動詞", 'prep': "介詞", 'det': "外名詞", 'noun': "名詞", 'num': "數詞"}
def scandef(e, spell, ident, coder=tex):
    synonyms = []
    antonyms = []
    samples = []
    explanation = ''
    if not('num' in e.attrib.keys()):
        num = 1
    else:
        num = e.attrib['num']
    if 'category' in e.attrib.keys():
        category = categories[e.attrib['category']]
    else:
        category = '雜詞'
    if 'supp' in e.attrib.keys():
        if '+' in e.attrib['supp']:
            temp = '時'
        else:
            temp = '常'
        category += '，'+ temp + '取' + categories[e.attrib['supp'].replace('+', '')]
    if 'spec' in e.attrib.keys():
        if '+' in e.attrib['spec']:
            temp = '時'
        else:
            temp = '常'
        category += '，' + temp + '戴' + categories[e.attrib['spec'].replace('+', '')]
    if 'epp' in e.attrib.keys():
        if '+' in e.attrib['epp']:
            temp = '時'
        else:
            temp = '常'
        category += '，' + temp +'引' + categories[e.attrib['epp'].replace('+', '')]
    if 'c-command' in e.attrib.keys():
        if '+' in e.attrib['c-command']:
            temp = '時'
        else:
            temp = '常'
        category += '，' + temp +'爲' + categories[e.attrib['epp'].replace('+', '')] + "制"
    explanation=textify(e, spell, ident)
    '''
    for child in e:
        if child.tag == 'exp':
            explanation = textify(child, spell, ident, coder)
        elif child.tag == 'samp':
            if 'source' in child.attrib.keys():
                _source = child.attrib['source']
            else:
                _source = ''
            samples += [(_source, textify(child, spell, ident, coder))]
        elif child.tag == 'syn':
            (temp, f) = search(child.attrib['ident'])
            root = temp.getroot()
            num0 = 1
            mspell = ''
            if 'num' in root.attrib.keys():
                num0 = root.attrib['num']
            for child0 in root:
                if child0.tag == 'spell':
                    mspell = child0.text
            synonyms +=  [(mspell, num0, child.attrib['ident'])]
        elif child.tag == 'ant':
            (temp, f) = search(child.attrib['ident'])
            root = temp.getroot()
            num0 = 1
            mspell = ''
            if 'num' in root.attrib.keys():
                num0 = root.attrib['num']
            for child0 in root:
                if child0.tag == 'spell':
                    mspell = child0.text
            antonyms += [(mspell, num0, child.attrib['ident'])
        '''
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
                    if  'ident' in root.attrib:
                        if root.attrib['ident'] == ident:
                            if root.tag == 'entry':
                                return (tree, p)
    return None

def updatexml(path):
    print(path)
    tree = etree.parse(path, parser)
    root = tree.getroot()
    if not('ident' in root.attrib.keys()):
        root.set('ident', '{}'.format(generateIdent()))
        tree.write(path)
    if not('num' in root.attrib.keys()):
        root.set('num', '1')
        num = '1'
    else:
        num = root.attrib['num']
    ident = root.attrib['ident']
    etree.ElementTree(tree.getroot()).write(path, pretty_print=True, encoding='utf-8')
def scanxml(tree):
    root = tree.getroot()
    num = root.attrib['num']
    ident = root.attrib['ident']
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
            elif child.tag == 'def':
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
            print('An error has been occured in {}'.format(p))
def collect_entries(code=tex):
        results = []
        for (path, dir, files) in os.walk('entries'):
            for filename in files:
                p = '{}/{}'.format(path, filename)
                ext = os.path.splitext(filename)[-1]
                if ext == '.xml':
                    results += [scanxml(etree.parse(p))]
        return sorted(results, key=lambda x: _spell(x[4], x[1]))
def build_db(conn):
    results = collect_entries(html)
    conn.execute("DROP TABLE IF EXISTS _alternative_spells;")
    conn.execute("DROP TABLE IF EXISTS _synonyms;")
    conn.execute("DROP TABLE IF EXISTS _antonyms;")
    conn.execute("DROP TABLE IF EXISTS _samples;")
    conn.execute("DROP TABLE IF EXISTS _explanations;")
    conn.execute("DROP TABLE IF EXISTS _words;")
    conn.execute("CREATE TABLE _words(_spell TEXT, _ident BIGINT);")
    conn.execute("CREATE TABLE _alternative_spells(_spell TEXT, _ident BIGINT);")
    conn.execute("CREATE TABLE _explanations(_category TEXT, _exp TEXT, _ident BIGINT, _exp_ident BIGSERIAL PRIMARY KEY);")
    conn.execute("CREATE TABLE _synonyms(_from BIGINT REFERENCES _explanations(_exp_ident), _dest BIGINT);")
    conn.execute("CREATE TABLE _antonyms(_from BIGINT REFERENCES _explanations(_exp_ident), _dest BIGINT);")
    conn.execute("CREATE TABLE _samples(_source TEXT, _sample TEXT, _exp BIGINT REFERENCES _explanations(_exp_ident));")
    for result in results:
        (root, num, spell, ident, alternative_spells, definitions) = result.values
        conn.execute('INSERT INTO _words(_spell, _ident) VALUES(\'{}\', {});'.format(spell, ident))
        for sp in alternative_spells:
            conn.execute("INSERT INTO _alternative_spells(_spell, _ident)  VALUES(\'{}\', {});".format(spell, ident))
        conn.commit()
        definition_txt = ''
        for d in sorted(definitions, key=itemgetter(0)):
            (numx, category, synonyms, antonyms, samples, explanation) = d
            exp_ident = 0
            for row in conn.execute("INSERT INTO _explanations(_exp, _category, _ident) VALUES(\'{}\', \'{}\', {}) RETURNING _exp_ident;".format(explanation, category, ident)).fetchall():
                exp_ident = row['_ident']
            for synonym in synonyms:
                conn.execute("INSERT INTO _synonyms(_from, _dest) VALUES ({}, {});".format(exp_ident, synonym[3]))
            for antonym in antonyms:
                conn.execute("INSERT INTO _synonyms(_from, _dest) VALUES ({}, {});".format(exp_ident, antonym[3]))
            for sample in samples:
                conn.execute("INSERT INTO _synonyms(_source, _sample, _exp) VALUES ({}, {});".format(sample[0], sample[1], exp_ident))
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
                sample_txt += '{}曰『{}』。'.format(sample[0], sample[1])

            definition_txt += "\\explain{{{}}}{{{}{}{}{}}}".format(category_txt, explanation, synonym_txt, antonym_txt, sample_txt)
        txt+= "\\entry{{{}}}{{{}}}{{{}{}{}}}{{{}}}".format(spell.replace('（', "").replace('）', ''), num, spells, definition_txt, cites, '')
    return txt
def initialize():
    global c
    if not c.unihan.is_bootstrapped:
        c.unihan.bootstrap()
initialize()

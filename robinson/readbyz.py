# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2021 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
import sys
import os
import string
import re

import convert
import reader
import readwhat

BYZTXT_REPODIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'byzantine-majority-text'))

BYZTXT_BETA_CODE_DIR = os.path.join(BYZTXT_REPODIR, 'textonly-beta-code')

BYZTXT_PARSED_DIR = os.path.join(BYZTXT_REPODIR, 'parsed')



comment_re = re.compile(r'#.*$')
comment_re_B = re.compile(r'\{B')
comment_re_NA = re.compile(r'\{N')

st_in_Byz = 0
st_in_NA = 1
st_in_B = 2

reUpperCaseBETA = re.compile(r'([A-Z])')
reMoveDiacriticsBETA = re.compile(r'\*([AEHIOUW])([\(\)][/=\\|]*)')
reMoveBreathingRhoBETA = re.compile(r'\*R([\(\)])')

MixedCaseBETAtoBETAtrans = string.maketrans("AaBbGgDdEeZzHhQqIiKkLlMmNnCcOoPpRrSsJjTtUuFfXxYyWw", "AABBGGDDEEZZHHQQIIKKLLMMNNCCOOPPRRSSSSTTUUFFXXYYWW")


def MixedCaseBETAtoBETAtranslate(str):
    return str.translate(MixedCaseBETAtoBETAtrans)

def MixedCaseBETAtoBETAtranslateWithStar(str):
    newstr = reUpperCaseBETA.sub(r'*\1', str).replace("^", "=")
    newstr = reMoveDiacriticsBETA.sub(r'*\2\1', newstr)
    newstr = reMoveBreathingRhoBETA.sub(r'*\1R', newstr)
    newstr = newstr.replace("(*", "*(").replace("(/*", "*(/").replace("(\\*", "*(\\").replace("(=*", "*(=").replace(")*", "*)").replace(")/*", "*)/").replace(")\\*", "*)\\").replace(")=*", "*)=")
    newstr = newstr.replace("+\\", "\\+").replace("+/","/+")
    newstr = newstr.replace("|=", "=|")
    return newstr.translate(MixedCaseBETAtoBETAtrans)


def b2u(s):
    w = MixedCaseBETAtoBETAtranslateWithStar(s) 
    return convert.beta2unicode(w)

def b2stripped(s):
    w = MixedCaseBETAtoBETAtranslateWithStar(s.replace("^","="))
    w = w.replace("=","").replace("/","").replace("\\","").replace("+","").replace("|","").replace("*","").replace("(","").replace(")","").replace(":","").replace(",","").replace(".","").replace(";","").replace("'","").replace("<","").replace(">","")
    return w

class Word:
    def __init__(self, prefix, surface):
	if prefix == "":
	    self.prefix = "."
	else:
	    self.prefix = prefix
	self.surface = surface
	self.parsing = ""
        self.strongs = ""

class Verse:
    def __init__(self):
        self.words = []
        self.chapter = 0
        self.verse = 0
	self.curword = 0


    def parse_line(self, line):
        line = re.sub(comment_re, "", line)
        if len(line.strip()) == 0:
            return False
        arr = line.strip().split()
        ch,v = arr[0].split(":")
        self.chapter = int(ch)
        self.verse = int(v)
        state = st_in_Byz
	prefix = ""
        for w in arr[1:]:
            if w[0] == "{":
                if w[1] == "N":
                    state = st_in_NA
                elif w[1] == "B":
                    state = st_in_B
                elif w[1] == "P":
		    assert w == "{P}"
		    prefix = w
                else:
                    raise "Unknown {-word '%'s in line '%s'" % (w, line)
            elif "}" in w:
                if state == st_in_NA or state == st_in_B:
                    state = st_in_Byz
		    prefix = ""
                else:
                    if len(w) > 1:
                        self.words.append(Word(prefix,w.replace("}","")))
			prefix = ""
            elif w == "-":
		if prefix != "":
		    prefix += " " + w
		else:
		    prefix = w
            else:
                if state == st_in_Byz:
                    if "{B" in w[1:]:
                        # This occurs twice, in Luke 9:22 and Mark
                        # 14:65. The {B is simply not separated by a space
                        # from the preceding material.
                        w = w.replace("{B","")
                        state = st_in_B
                    elif "{N" in w[1:]:
                        assert False, "ERROR: We should not be able to get here. Revise logic. w = '%s'" % w
                        # This is what to do if we ever encounter this
                        #w = w.replace("{N","")
                        #state = st_in_NA
                    
                    self.words.append(Word(prefix,w))
		    prefix = ""
                else:
                    pass # In st_in_NA or st_in_B: Discard words...

                    
        return True

    def pretty(self, bookname, booknumber):
        wds = []
        for w in self.words:
            wds.append(b2u(w.surface))
            
        print ("%s %d:%d %s" % (bookname, self.chapter, self.verse, " ".join(wds))).encode("utf-8")

    def linear(self, bookname, booknumber, filename):
        for w in self.words:
            print ("%s %02d:%02d %s %s" % (filename, self.chapter, self.verse, b2u(w.surface), w.parsing)).encode("utf-8")

    def linear_all(self, f, bookname, booknumber, filename):
        for w in self.words:
            print >> f, ("%s %02d:%02d %s %s %s %s %s" % (filename, self.chapter, self.verse, w.prefix, MixedCaseBETAtoBETAtranslateWithStar(w.surface), b2u(w.surface), w.parsing, w.strongs)).encode("utf-8")

    def linear_stripped(self, bookname, booknumber, filename):
        for w in self.words:
            print ("%s %02d:%02d %s" % (filename, self.chapter, self.verse, b2stripped(w.surface))).encode("utf-8")


class Book:
    def __init__(self, indir, filename):
	self.versedict = {}
        self.verses = []
        self.filename = filename
        self.olbbook = filename.split(".")[0]
        self.filename2book(filename)
        self.read(indir, filename)

    def read(self, indir, filename):
        f = open(os.path.join(indir, filename))
        for line in f.readlines():
            v = Verse()
            if v.parse_line(line):
                self.verses.append(v)
		self.versedict["%s:%s" % (v.chapter, v.verse) ] = v
            else:
                del v
        f.close()

        for v in self.verses:
            if v.verse == 1:
                v.words[0].prefix = "{C}"

    def filename2book(self, filename):
        bk = filename.split(".")[0]
        if bk == "MT":
            self.bookname = "Matthew"
            self.booknumber = 1
        elif bk == "MR":
            self.bookname = "Mark"
            self.booknumber = 2
        elif bk == "LU":
            self.bookname = "Luke"
            self.booknumber = 3
        elif bk == "JOH":
            self.bookname = "John"
            self.booknumber = 4
        elif bk == "AC":
            self.bookname = "Acts"
            self.booknumber = 5
        elif bk == "RO":
            self.bookname = "Romans"
            self.booknumber = 6
        elif bk == "1CO":
            self.bookname = "I_Corinthians"
            self.booknumber = 7
        elif bk == "2CO":
            self.bookname = "II_Corinthians"
            self.booknumber = 8
        elif bk == "GA":
            self.bookname = "Galatians"
            self.booknumber = 9
        elif bk == "EPH":
            self.bookname = "Ephesians"
            self.booknumber = 10
        elif bk == "PHP":
            self.bookname = "Philippians"
            self.booknumber = 11
        elif bk == "COL":
            self.bookname = "Colossians"
            self.booknumber = 12
        elif bk == "1TH":
            self.bookname = "I_Thessalonians"
            self.booknumber = 13
        elif bk == "2TH":
            self.bookname = "II_Thessalonians"
            self.booknumber = 14
        elif bk == "1TI":
            self.bookname = "I_Timothy"
            self.booknumber = 15
        elif bk == "2TI":
            self.bookname = "II_Timothy"
            self.booknumber = 16
        elif bk == "TIT":
            self.bookname = "Titus"
            self.booknumber = 17
        elif bk == "PHM":
            self.bookname = "Philemon"
            self.booknumber = 18
        elif bk == "HEB":
            self.bookname = "Hebrews"
            self.booknumber = 19
        elif bk == "JAS":
            self.bookname = "James"
            self.booknumber = 20
        elif bk == "1PE":
            self.bookname = "I_Peter"
            self.booknumber = 21
        elif bk == "2PE":
            self.bookname = "II_Peter"
            self.booknumber = 22
        elif bk == "1JO":
            self.bookname = "I_John"
            self.booknumber = 23
        elif bk == "2JO":
            self.bookname = "II_John"
            self.booknumber = 24
        elif bk == "3JO":
            self.bookname = "III_John"
            self.booknumber = 25
        elif bk == "JUDE":
            self.bookname = "Jude"
            self.booknumber = 26
        elif bk == "RE":
            self.bookname = "Revelation"
            self.booknumber = 27
        else:
            print "Unknown bookname: '", bk, "'"
            sys.exit()

    def pretty(self):
        for v in self.verses:
            v.pretty(self.bookname, self.booknumber)

    def linear(self):
        for v in self.verses:
            v.linear(self.bookname, self.booknumber, self.olbbook)

    def linear_all(self, f):
        for v in self.verses:
	    v.linear_all(f, self.bookname, self.booknumber, self.olbbook)

    def linear_stripped(self):
        for v in self.verses:
            v.linear_stripped(self.bookname, self.booknumber, self.olbbook)


book_list_OLB = ["MT", "MR", "LU", "JOH", "AC", "RO", "1CO", "2CO",
                 "GA", "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI",
                 "TIT", "PHM", "HEB", "JAS", "1PE", "2PE", "1JO", "2JO", "3JO",
                 "JUDE", "RE"]

class ByzReader:
    def __init__(self):
        self.books = []
	self.bookdict = {}

    def read_book(self, indir, filename):
        bk = Book(indir, filename + ".CCT")
        sys.stderr.write("%s\n" % filename)
        self.books.append(bk)
	self.bookdict[filename] = bk

    def read_MT(self):
        self.read_book(BYZTXT_BETA_CODE_DIR, "MT")

    def read_NT(self):
        for bk in book_list_OLB:
            self.read_book(BYZTXT_BETA_CODE_DIR, bk)

    def pretty(self):
        for bk in self.books:
            bk.pretty()

    def linear(self):
        for bk in self.books:
            bk.linear()

    def linear_all(self, f):
        for bk in self.books:
            bk.linear_all(f)

    def linear_stripped(self):
        for bk in self.books:
            bk.linear_stripped()


def read_MT():
    rd = ByzReader()
    rd.read_MT()
    return rd

def read_NT():
    rd = ByzReader()
    rd.read_NT()
    return rd

def read_NT_pretty():
    rd = read_NT()
    rd.pretty()

def read_NT_linear():
    rd = read_NT()
    rd.linear()

def read_NT_linear_stripped():
    rd = read_NT()
    rd.linear_stripped()

def read_Parsed_MT():
    rd = reader.Reader(BYZTXT_PARSED_DIR, 'UB5')
    rd.read_MT(reader.read_first_variant_only, reader.read_UMAR_encoding)
    return rd

def read_Parsed_NT():
    rd = reader.Reader(BYZTXT_PARSED_DIR, 'UB5')
    rd.read_NT(readwhat.normalize("text_only"), reader.read_UMAR_encoding)
    return rd

def read_MT_compare():
    rdprs = read_Parsed_MT()
    rdacc = read_MT()
    rdprs.apply_predicate(mycompare_predicate, rdacc)
    f = open("byzantine-MT.txt", "w")
    rdacc.linear_all(f)
    f.close()

def mycompare_predicate(OLB_bookname, chapter, verse, parsedword, rdacc):
    try:
	myverse = rdacc.bookdict[OLB_bookname].versedict["%s:%s" % (chapter, verse)]
    except:
	raise Exception("ERROR: Could not find %s %s:%s in accented text." % (OLB_bookname, chapter, verse))
	return False

    try:
	w = myverse.words[myverse.curword]
    except:
	raise Exception("%s %s:%s:%s '%s' %s" % (OLB_bookname, chapter, verse, myverse.curword, myverse.curword, [w.surface for w in myverse.words]))
    word_surface = w.surface
    stripped_word_BETA = b2stripped(word_surface)
    stripped_word_OLB = convert.BETAtoUMARtranslate(stripped_word_BETA)

    parsed_word_surface = parsedword.surface

    #print "UP200: parsed_word_surface = '%s', stripped_word_OLB = '%s', stripped_word_BETA = '%s'" % (parsed_word_surface, stripped_word_OLB, stripped_word_BETA)

    if stripped_word_OLB == parsed_word_surface:
	w.parsing = parsedword.parsing
        w.strongs = parsedword.getStrongs()
        #print >> sys.stderr, "SUCCESS: %s == %s" % (stripped_word_OLB, parsed_word_surface)
    else:
	w.parsing = "NOPARSE"
        w.strongs = "9999"
	print >> sys.stderr, "ERROR: strings do not match for %s %s:%s: '%s' != '%s'" % (OLB_bookname, chapter, verse, stripped_word_OLB, parsed_word_surface)

    # Increment iterator
    myverse.curword += 1

    return True


def read_NT_compare():
    rdprs = read_Parsed_NT()
    rdacc = read_NT()
    sys.stderr.write("... Comparing parsed and unparsed, annotating unparsed with parsing...\n")
    rdprs.apply_predicate(mycompare_predicate, rdacc)
    f = open("byzantine.txt", "w")
    rdacc.linear_all(f)
    f.close()

def read_MT_linear_all():
    rdacc = read_MT()
    f = open("byzantine_MT.txt", "w")
    rdacc.linear_all(f)
    f.close()
    
def read_NT_linear_all():
    rdacc = read_NT()
    f = open("byzantine_all.txt", "w")
    rdacc.linear_all(f)
    f.close()
    

if __name__ == '__main__':
    #read_MT()
    #read_MT_linear_all()
    #read_NT_linear_all()
    #read_NT()
    #read_RE()
    #read_NT_pretty()
    #read_NT_linear()
    #read_NT_linear_stripped()
    #read_MT_compare()
    read_NT_compare()


        

# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals, print_function

import string
import sys
from verse import Verse
from chapter import Chapter
from variant import *
from kind import *
import word
import re

chapter_verse_re = re.compile(r'^\d+:\d+$')



myverseletters = ["a", "b", "c", "d", "e"]


bookdict = {
    # OLB, unbound, enum, dkabbrev, BibleWorks, OSIS, longEnglish
    "1.Mosebog" : ("GE", "01O", "Genesis", "1. Mos", "", "Gen", "Genesis"),
    "2.Mosebog" : ("EX", "02O", "Exodus", "2. Mos", "", "Exod", "Exodus"),
    "3.Mosebog" : ("LE", "03O", "Leviticus", "3. Mos", "", "Lev", "Leviticus"),
    "4.Mosebog" : ("NU", "04O", "Numbers", "4. Mos", "", "Num", "Numbers"),
    "5.Mosebog" : ("DE", "05O", "Deuteronomy", "5. Mos", "", "Deut", "Deuteronomy"),
    "Josua" : ("JOS", "06O", "Joshua", "Jos", "", "Josh", "Joshua"),
    "Dommer" : ("JUD", "07O", "Judges", "Dom", "", "Judg", "Judges"),
    "Rut" : ("RU", "08O", "Ruth", "Rut", "", "Ruth", "Ruth"),
    "1.Samuel" : ("1SA", "09O", "I_Samuel", "1. Sam", "", "1Sam", "1 Samuel"),
    "2.Samuel" : ("2SA", "10O", "II_Samuel", "2. Sam", "", "2Sam", "2 Samuel"),
    "Første Kongebog" : ("1KI", "11O", "I_Kings", "1. Kong", "", "1Kgs", "1 Kings"),
    "Anden Kongebog" : ("2KI", "12O", "II_Kings", "2. Kong", "", "2Kgs", "2 Kings"),
    "Første Krønikebog" : ("1CH", "13O", "I_Chronicles", "1. Krøn", "", "1Chr", "1 Chronicles"),
    "Anden Krønikebog" : ("2CH", "14O", "II_Chronicles", "2. Krøn", "", "2Chr", "2 Chronicles"),
    "Ezra" : ("EZR", "15O", "Ezra", "Ezr", "", "Ezra", "Ezra"),
    "Nehemias" : ("NE", "16O", "Nehemiah", "Neh", "", "Neh", "Nehemiah"),
    "Ester" : ("ES", "17O", "Esther", "Est", "", "Esth", "Esther"),
    "Job" : ("JOB", "18O", "Job", "Job", "", "Job", "Job"),
    "Salmerne" : ("PS", "19O", "Psalms", "Sl", "", "Ps", "Psalms"), # Salmerne is the heading for the entire book
    "Salme" : ("PS", "19O", "Psalms", "Sl", "", "Ps", "Psalms"), # Salme is what is at the begining of each chapter
    "Ordsprogene" : ("PR", "20O", "Proverbs", "Ordsp", "", "Prov", "Proverbs"),
    "Prædikeren" : ("EC", "21O", "Ecclesiastes", "Præd", "", "Eccl", "Ecclesiastes"),
    "Højsangen" : ("SO", "22O", "Canticles", "Højs", "", "Song", "Song of Solomon"),
    "Esajas" : ("ISA", "23O", "Isaiah", "Es", "", "Isa", "Isaiah"),
    "Jeremias" : ("JER", "24O", "Jeremiah", "Jer", "", "Jer", "Jeremiah"),
    "Klagesangene" : ("LA", "25O", "Lamentations", "Klag", "", "Lam", "Lamentations"),
    "Ezekiel" : ("EZE", "26O", "Ezekiel", "Ezek", "", "Ezek", "Ezekiel"),
    "Daniel" : ("DA", "27O", "Daniel", "Dan", "", "Dan", "Daniel"),
    "Hoseas" : ("HO", "28O", "Hosea", "Hos", "", "Hos", "Hosea"),
    "Joel" : ("JOE", "29O", "Joel", "Joel", "", "Joel", "Joel"),
    "Amos" : ("AM", "30O", "Amos", "Amos", "", "Amos", "Amos"),
    "Obadias" : ("OB", "31O", "Obadiah", "Obad", "", "Obad", "Obadiah"),
    "Jonas" : ("JON", "32O", "Jonah", "Jon", "", "Jonah", "Jonah"),
    "Mikas" : ("MIC", "33O", "Micah", "Mik", "", "Mic", "Micah"),
    "Nahum" : ("NA", "34O", "Nahum", "Nah", "", "Nah", "Nahum"),
    "Habakkuk" : ("HAB", "35O", "Habakkuk", "Hab", "", "Hab", "Habakkuk"),
    "Zefanias" : ("ZEP", "36O", "Zephaniah", "Zef", "", "Zeph", "Zephaniah"),
    "Haggaj" : ("HAG", "37O", "Haggai", "Hag", "", "Hag", "Haggai"),
    "Zakarias" : ("ZEC", "38O", "Zechariah", "Zak", "", "Zech", "Zechariah"),
    "Malakias" : ("MAL", "39O", "Malachi", "Mal", "", "Mal", "Malachi"),
    "Matt." : ("MT", "40N", "Matthew", "Matt", "Mat", "Matt", "Matthew"),
    "Markus" : ("MR", "41N", "Mark", "Mark", "Mar", "Mark", "Mark"),
    "Lukas" : ("LU", "42N", "Luke", "Luk", "Luk", "Luke", "Luke"),
    "Johannes" : ("JOH", "43N", "John", "Joh", "Joh", "John", "John"),
    "Apostlenes Gerninger" : ("AC", "44N", "Acts", "ApG", "Act", "Acts", "Acts"),
    "Romerne" : ("RO", "45N", "Romans", "Rom", "Rom", "Rom", "Romans"),
    "1.Korinterne" : ("1CO", "46N", "I_Corinthians", "1.Kor", "1Co", "1Cor", "1 Corinthians"),
    "2.Korinterne" : ("2CO", "47N", "II_Corinthians", "2. Kor", "2Co", "2Cor", "2 Corinthians"),
    "Galaterne" : ("GA", "48N", "Galatians", "Gal", "Gal", "Gal", "Galatians"),
    "Efeserne" : ("EPH", "49N", "Ephesians", "Ef", "Eph", "Eph", "Ephesians"),
    "Filipperne" : ("PHP", "50N", "Philippians", "Fil", "Phi", "Phil", "Philippians"),
    "Kolossenserne" : ("COL", "51N", "Colossians", "Kol", "Col", "Col", "Colossians"),
    "1.Tessalonikerne" : ("1TH", "52N", "I_Thessalonians", "1. Tess", "1Th", "1Thess", "1 Thessalonians"),
    "2.Tessalonikerne" : ("2TH", "53N", "II_Thessalonians", "2. Tess", "2Th", "2Thess", "2 Thessalonians"),
    "1.Timoteus" : ("1TI", "54N", "I_Timothy", "1. Tim", "1Ti", "1Tim", "1 Timothy"),
    "2.Timoteus" : ("2TI", "55N", "II_Timothy", "2. Tim", "2Ti", "2Tim", "2 Timothy"),
    "Titus" : ("TIT", "56N", "Titus", "Tit", "Tit", "Titus", "Titus"),
    "Filemon" : ("PHM", "57N", "Philemon", "Filem", "Phm", "Phlm", "Philemon"),
    "Hebræerne" : ("HEB", "58N", "Hebrews", "Hebr", "Heb", "Heb", "Hebrews"),
    "Jakob" : ("JAS", "59N", "James", "Jak", "Jam", "Jas", "James"),
    "1.Peter" : ("1PE", "60N", "I_Peter", "1. Pet", "1Pe", "1Pet", "1 Peter"),
    "2.Peter" : ("2PE", "61N", "II_Peter", "2. Pet", "2Pe", "2Pet", "2 Peter"),
    "1.Johannes" : ("1JO", "62N", "I_John", "1. Joh", "1Jo", "1John", "1 John"),
    "2.Johannes" : ("2JO", "63N", "II_John", "2. Joh", "2Jo", "2John", "2 John"),
    "3.Johannes" : ("3JO", "64N", "III_John", "3. Joh", "3Jo", "3John", "3 John"),
    "Judas" : ("JUDE", "65N", "Jude", "Jud", "Jud", "Jude", "Jude"),
    "Aabenbaringen" : ("RE", "66N", "Revelation", "Åb", "Rev", "Rev", "Revelation"),
}

OLB2OSIS_dict = { }
OLB2LongEnglish_dict = { }


for key in bookdict:
    (OLB, unbound, enum, dkabbrev, BibleWorks, OSIS, longEnglish) = bookdict[key]
    OLB2OSIS_dict[OLB] = OSIS
    OLB2LongEnglish_dict[OLB] = longEnglish






class Sentence:
    def __init__(self, starting_monad):
	self.starting_monad = starting_monad
	self.ending_monad = starting_monad

    def set_ending_monad(self, ending_monad):
	self.ending_monad = ending_monad

    def writeMQL(self, f, bUseOldStyle):
        print("CREATE OBJECT", file=f)
        print("FROM MONADS={%d-%d}" % (self.starting_monad, self.ending_monad), file=f)
        if bUseOldStyle:
            OT = "Sentence"
        else:
            OT = ""
        print("[%s]" % OT, file=f)

        if bUseOldStyle:
            print("GO\n", file=f)
        else:
            print("", file=f)

class Book:
    def __init__(self, filename):
        self.filename = filename
        self.parse_filename(filename)
        self.chapter = 0
        self.verse = -1
        self.chapters = []
        self.verses = []
	self.sentences = []
        self.verse_dict = {}
        #print(filename)

    def parse_filename(self, filename):
        path_ingridients = filename.split("/")
        bk = path_ingridients[-1].split(".")[0].upper()
        self.OLBbook = bk
        self.OSISBook = OLB2OSIS_dict[self.OLBbook]
        self.LongEnglishBook = OLB2LongEnglish_dict[self.OLBbook]

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
            print("Unknown bookname: '", bk, "'")
            sys.exit()

    def read(self, start_monad, read_what):
        self.start_monad = start_monad
        self.chapter_first_monad = start_monad
        self.end_monad = start_monad - 1
        f = self.open_file()
        lines = f.readlines()
        f.close()
        self.parse_lines(lines, read_what)
        return self.end_monad

    def read_linear(self, start_monad):
        self.start_monad = start_monad
        self.chapter_first_monad = start_monad
        self.end_monad = start_monad - 1
        f = self.open_file()
        lines = f.readlines()
        f.close()
        self.parse_lines_linear(lines)
        return self.end_monad

    def parse_lines_linear(self, lines):
        for line in lines:
            line = line.replace("\r", "").replace("\n", "")
            myarr = line.split(" ")
            [mybook, mychapterverse, mybreak_kind, mysurface, myqere, mytag, mystrongs] = myarr[0:7]            
            strongslemma = ""
            ANLEXlemma = ""
            [strongslemma, ANLEXlemma] = " ".join(myarr[7:]).split(" ! ")
            self.process_linear_verse(mychapterverse)
            self.process_linear_word(mybreak_kind, mysurface, myqere, mytag, mystrongs, strongslemma, ANLEXlemma)
        self.parseChapter(self.chapter, self.end_monad)

    def process_linear_verse(self, mychapterverse):
        myarr = mychapterverse[0:mychapterverse.find(".")].split(":")
        mychapter = int(myarr[0])
        myverse = int(myarr[1])
        chapter_end = self.end_monad
        self.end_monad += 1
        if self.chapter != mychapter:
            if self.chapter <> 0:
                self.parseChapter(self.chapter, chapter_end)
            self.chapter = mychapter
        if self.verse != myverse:
            self.verse = myverse
            verse = Verse([], self.bookname, self.booknumber)
            verse.chapter = mychapter
            verse.verse = myverse
            verse.first_monad = self.end_monad
            verse.last_monad = self.end_monad
            self.verses.append(verse)


    def process_linear_word(self, mybreak_kind, mysurface, myqere, mytag, mystrongs, strongslemma, ANLEXlemma):
        w = word.Word(self.end_monad, variant_none)
        w.break_kind = mybreak_kind
        w.surface = mysurface
        w.qere = myqere
        w.accented_surface = mysurface
        w.parsing = mytag
        w.Strongs1 = mystrongs
        w.strongslemma = strongslemma
        w.ANLEXlemma = ANLEXlemma
        self.verses[-1].words.append(w)
        self.verses[-1].last_monad = self.end_monad
        

    def open_file(self):
        f = open(self.filename, "r")
        return f
            
    def parse_lines(self, lines, read_what):
        verse_lines = []
        for ln in lines:
            arr = ln.split()
            if len(arr) > 0 and chapter_verse_re.match(arr[0]) != None:
                if not len(verse_lines) == 0:
                    self.parseVerse(verse_lines, self.end_monad + 1, 0, read_what)
                    del verse_lines
                    verse_lines = []
            verse_lines.append(ln)
        if not len(verse_lines) == 0:
            self.parseVerse(verse_lines, self.end_monad + 1, 1, read_what)

    def parseVerse(self, verse_lines, first_monad, is_last_verse_of_book, read_what):
        verse = Verse(verse_lines, self.bookname, self.booknumber)
        self.verses.append(verse)
        chapter_end = self.end_monad
        self.end_monad = verse.parse(first_monad, read_what)
        chapter = verse.chapter
        if is_last_verse_of_book:
            chapter_end = self.end_monad
            self.parseChapter(self.chapter, chapter_end)
        elif self.chapter <> chapter:
            if self.chapter <> 0:
                self.parseChapter(self.chapter, chapter_end)
            self.chapter = chapter


    def parseChapter(self, chapter, chapter_end_monad):
        ch = Chapter(self.chapter_first_monad, chapter_end_monad, chapter, self.bookname)
        self.chapters.append(ch)
        self.chapter_first_monad = chapter_end_monad + 1

    def parse_sentences(self):
	words = []
	for v in self.verses:
	    words.extend(v.words)
	del self.sentences
	self.sentences = []
	cur_monad = self.start_monad
	self.sentences.append(Sentence(cur_monad))
	for w in words:
	    if w.ends_sentence():
		ending_monad = w.monad
		self.sentences[-1].set_ending_monad(ending_monad)
		if ending_monad != self.end_monad:
		    self.sentences.append(Sentence(ending_monad+1))

	# End the last sentence if the last word of the book 
	# did not have an end-of-sentence punctuation
	if self.sentences[-1].ending_monad != self.end_monad:
	    self.sentences[-1].set_ending_monad(self.end_monad)

    def writeVersesMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print("CREATE OBJECTS WITH OBJECT TYPE [Verse]", file=f)
        for v in self.verses:
            v.writeMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print("GO", file=f)
        print("", file=f)

    def writeSentencesMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print("CREATE OBJECTS WITH OBJECT TYPE [Sentence]", file=f)
        for s in self.sentences:
            s.writeMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print("GO", file=f)
        print("", file=f)

    def writeWordsMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print("CREATE OBJECTS WITH OBJECT TYPE [Word]", file=f)
        for v in self.verses:
            v.writeWordsMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print("GO", file=f)
        print("", file=f)

    def writeChaptersMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print("CREATE OBJECTS WITH OBJECT TYPE [Chapter]", file=f)
        for ch in self.chapters:
            ch.writeMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print("GO", file=f)
        print("", file=f)

    def writeBookMQL(self, f, bUseOldStyle):
        print("CREATE OBJECT", file=f)
        print("FROM MONADS = {", self.start_monad, "-", self.end_monad, "}", file=f)
        print("[Book", file=f)
        print("  book:=" + self.bookname + ";", file=f)
        print("]", file=f)
        print("GO", file=f)
        print("", file=f)

    def writeMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print("BEGIN TRANSACTION GO", file=f)
        self.writeBookMQL(f, bUseOldStyle)
        self.writeChaptersMQL(f, bUseOldStyle)
        self.writeVersesMQL(f, bUseOldStyle)
        self.writeSentencesMQL(f, bUseOldStyle)
        self.writeWordsMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print("COMMIT TRANSACTION GO", file=f)

    def writeSFM(self, f, cur_monad):
        for v in self.verses:
            cur_monad = v.writeSFM(f, cur_monad)
        return cur_monad

    def getWords(self):
        result = []
        for v in self.verses:
            result.extend(v.getWords())
        return result

    def addToVerseDict(self, myverse):
        ref = myverse.getRef()

        try:
            self.verse_dict[ref]
        except KeyError:
            self.verse_dict[ref] = []
        self.verse_dict[ref].append(myverse)

    def addVersesToVerseDict(self):
        for v in self.verses:
            self.addToVerseDict(v)

    def getVersesByRef(self, ref):
        try:
            return self.verse_dict[ref]
        except KeyError:
            return None

    def getVerseCopy(self, whverse):
        ref = whverse.getRef()
        mylist = self.verse_dict[ref]
        if len(mylist) == 0:
            raise Exception("Error: On ref %s: mylist is empty" % ref)
        elif len(mylist) == 1:
            return ""
        else:
            index = 0
            for v in mylist:
                if v is whverse:
                    return myverseletters[index]
                index += 1
            raise Exception("Error: On ref %s: whverse is not in list!" % ref)


    def write_MORPH_style_to_file(self, fout, encodingStyle):
        self.addVersesToVerseDict()
        for whverse in self.verses:
            whverse.write_MORPH_style(fout, self.getVerseCopy(whverse), encodingStyle)

    def write_StrippedLinear(self, f):
        self.addVersesToVerseDict()
        for whverse in self.verses:
            whverse.write_StrippedLinear(f, self.getVerseCopy(whverse))

    def write_WHLinear(self, f):
        self.addVersesToVerseDict()
        for whverse in self.verses:
            whverse.write_WHLinear(f, self.getVerseCopy(whverse))

    def write_Linear(self, filename):
        self.addVersesToVerseDict()
        f = open(filename, "w")
        for whverse in self.verses:
            whverse.write_Linear(f, self.getVerseCopy(whverse))
        f.close()

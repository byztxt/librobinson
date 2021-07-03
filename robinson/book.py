import string
import sys
from verse import *
from chapter import *
from variant import *
from kind import *
import word
from booknames import *

myverseletters = ["a", "b", "c", "d", "e", "f", "g"]

verse_re = re.compile(r'\(?(\d+):(\d+)\)?')

class Book:
    def __init__(self, filename, encoding):
        self.filename = filename
        self.parse_filename(filename)
        self.chapter = 0
        self.ch = 0
        self.vs = 0
        self.verse = -1
        self.chapters = []
        self.verses = []
        self.verse_dict = {}
        self.variant = variant_none
        self.encoding = encoding

    def parse_filename(self, filename):
        path_ingridients = filename.split("/")
        bk = path_ingridients[-1].split(".")[0].upper()
	self.OLB_bookname = bk
	try:
	    (self.bookname, self.booknumber) = OLB2More[bk]
	except:
            print "Unknown bookname: '%s'" % bk
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
            mybook = myarr[0]
            mychapterverse = myarr[1]
            mysurface = myarr[2]
            mytag = myarr[3]
            mystrongs = myarr[4]
            strongslemma = ""
            ANLEXlemma = ""
            if len(myarr) > 5:
                whatamIdoing = kStrongs
                strongslemmas = []
                ANLEXlemmas = []
                for mystr in myarr[5:]:
                    if mystr == "!":
                        whatamIdoing = kANLEX
                    else:
                        if whatamIdoing == kStrongs:
                            strongslemmas.append(mystr)
                        else:
                            ANLEXlemmas.append(mystr)
                strongslemma = " ".join(strongslemmas)
                ANLEXlemma = " ".join(ANLEXlemmas)
            self.process_linear_verse(mychapterverse)
            self.process_linear_word(mysurface, mytag, mystrongs, strongslemma, ANLEXlemma)
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
            verse = Verse([], self.bookname, self.booknumber, self.encoding)
            verse.chapter = mychapter
            verse.verse = myverse
            verse.first_monad = self.end_monad
            verse.last_monad = self.end_monad
            self.verses.append(verse)


    def process_linear_word(self, mysurface, mytag, mystrongs, strongslemma, ANLEXlemma):
        w = word.Word(self.end_monad, variant_none, self.encoding)
        w.surface = mysurface
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
	all = "\n".join(lines)

        if self.OLB_bookname == "MT":
            # Occurs in ByzParsed Matthew
            all = all.replace("23:13 (23:14)", "23:13").replace("23:14 (23:13)", "23:14")
        elif self.OLB_bookname == "RE":
            # Revelation 17:8 was treated as it was because Dr. Robinson
            # uses Online Bible for DOS himself, and 
            # OLB for DOS has a limit on how many words can be in a verse.
            # This one is just particularly long, and breaks the barrier
            # on OLB for DOS.
            
            # All other (ch:vs) should probably be ignored.
            all = all.replace("(17:8)", "$@!@$").replace("17:8", "").replace("$@!@$", " 17:8 ")

        words = []

        mystack = []

        chvs = ""

	for w in all.split():
	    if recognize(w) in [kind_verse, kind_parens]:
                chvs = w

	    if w == "M5:":
		mystack.append(":M5")
	    elif w == "M6:":
		mystack.append(":M6")
	    elif w == "VAR:":
		mystack.append(":END")
	    elif w in [":M5", ":M6", ":END"]:
		end_of_stack = mystack[-1]
		mystack = mystack[:-1]
		if w != end_of_stack:
		    print "UP310: %s end_of_stack = '%s', w = '%s', line_words = %s" % (self.bookname, end_of_stack, w, line_words)
		    #
		    # NOTE: They are not balanced in the text, 
		    # so let's not try...
		    #
		    raise "Error! M5/M6/VAR-END not balanced..."
		    pass
	    else:
		if len(mystack) == 0:
		    words.append(w)
		else:
		    pass

        overall_text = " ".join(words)

        if text_variant_strongs_parsing_re.search(overall_text) != None:
            overall_text = text_variant_strongs_parsing_re.sub(r'| \1\3 | \2\3 | ', overall_text)

        if text_strongs_varparsing_varparsing_re.search(overall_text) != None:
            overall_text = text_strongs_varparsing_varparsing_re.sub(r'| \1\2 | \1\3 | ', overall_text)

        if text_strongs_vartext_varstrongs_parsing.search(overall_text) != None:
            overall_text = text_strongs_vartext_varstrongs_parsing.sub(r'| \1 \3 | \2 \3 | ', overall_text)
            

        # In Romans 16:27 of WH, we find the line ends with "{HEB}|".
        # We need this to be "{HEB} |".
        overall_text = overall_text.replace("}|", "} |")

        words = []

        for wd in overall_text.split():
            if wd == "|":
                if self.variant == variant_none:
                    self.variant = variant_first
                elif self.variant == variant_first:
                    self.variant = variant_second
                elif self.variant == variant_second:
                    self.variant = variant_none
                else:
                    raise Exception("Error: Unknown self.variant: %s" % self.variant)
            elif recognize(wd) == kind_parens:
                # Remove parens altogether
                pass
            else:
                if self.variant == variant_none:
                    words.append(wd)
                elif self.variant == variant_first:
                    if read_what == reader.read_first_variant_only:
                        words.append(wd)
                    else:
                        pass
                elif self.variant == variant_second:
                    if read_what == reader.read_second_variant_only:
                        words.append(wd)
                    else:
                        pass
                else:
                    raise Exception("Error: Unknown variant: %s" % self.variant)
            

	verses = [] # List of lists of strings

        for wd in words:
	    if recognize(wd) == kind_verse:
                (ch,vs) = verse_re.findall(wd)[0]
                verses.append([])
                self.ch = ch
                self.vs = vs
                verses[-1].append(wd)
            else:
                verses[-1].append(wd)
                    
                        

	LAST_VERSE_INDEX = len(verses) - 1

        for index in xrange(0, len(verses)):
	    bIsLastVerseOfBook = index == LAST_VERSE_INDEX
	    self.parseVerse(verses[index], self.end_monad + 1, bIsLastVerseOfBook, read_what)

    def parseVerse(self, verse_lines, first_monad, is_last_verse_of_book, read_what):
        verse = Verse(verse_lines, self.bookname, self.booknumber, self.encoding)
        self.verses.append(verse)
        chapter_end = self.end_monad
        self.end_monad = verse.parse(first_monad)
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

                

    def writeVersesMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print >>f, "CREATE OBJECTS WITH OBJECT TYPE [Verse]"
        for v in self.verses:
            v.writeMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print >>f, "GO"
        print >>f, ""

    def writeWordsMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print >>f, "CREATE OBJECTS WITH OBJECT TYPE [Word]"
        for v in self.verses:
            v.writeWordsMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print >>f, "GO"
        print >>f, ""

    def writeChaptersMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print >>f, "CREATE OBJECTS WITH OBJECT TYPE [Chapter]"
        for ch in self.chapters:
            ch.writeMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print >>f, "GO"
        print >>f, ""

    def writeBookMQL(self, f, bUseOldStyle):
        print >>f, "CREATE OBJECT"
        print >>f, "FROM MONADS = {", self.start_monad, "-", self.end_monad, "}"
        print >>f, "[Book"
        print >>f, "  book:=" + self.bookname + ";"
        print >>f, "]"
        print >>f, "GO"
        print >>f, ""

    def writeMQL(self, f, bUseOldStyle):
        if not bUseOldStyle:
            print >>f, "BEGIN TRANSACTION GO"
        self.writeBookMQL(f, bUseOldStyle)
        self.writeChaptersMQL(f, bUseOldStyle)
        self.writeVersesMQL(f, bUseOldStyle)
        self.writeWordsMQL(f, bUseOldStyle)
        if not bUseOldStyle:
            print >>f, "COMMIT TRANSACTION GO"

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

    def applyLemma(self, mapping, lemma_kind):
        words = self.getWords()
        for w in words:
            w.applyLemma(mapping, lemma_kind)

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


    def write_MORPH_style(self, filename, encodingStyle):
        f = open(filename, "w")
        for whverse in self.verses:
            whverse.write_MORPH_style(f, self.getVerseCopy(whverse), encodingStyle)
        f.close()

    def write_subset_MORPH_style(self, f, word_predicate, manualanalyses, encodingStyle):
        for whverse in self.verses:
            whverse.write_subset_MORPH_style(f, self.getVerseCopy(whverse), word_predicate, manualanalyses, encodingStyle)
            
    def write_StrippedLinear(self, filename):
        self.addVersesToVerseDict()
        f = open(filename, "w")
        for whverse in self.verses:
            whverse.write_StrippedLinear(f, self.getVerseCopy(whverse))
        f.close()

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

    def apply_predicate(self, pred, extra):
	for verse in self.verses:
	    verse.apply_predicate(self.OLB_bookname, pred, extra)

import string
import re
from word import *
from variant import *
from kind import *
import reader

 
text_variant_strongs_parsing_re= re.compile(r'\|\s+([a-z\[\]]+)\s+\|\s+([a-z\[\]]+)\s+\|([0-9\s]+\{[A-Z0-9\-]+\})\s*')

text_strongs_varparsing_varparsing_re = re.compile(r'(\s+[a-z\[\]]+\s+[0-9]+\s+)\|\s+(\{[A-Z0-9\-]+\})\s+\|\s+(\{[A-Z0-9\-]+\})\s+')

text_strongs_vartext_varstrongs_parsing = re.compile(r'\|\s+([a-z\[\]]+\s+[0-9]+)\s+\|\s+([a-z\[\]]+\s+[0-9]+)\s+\|\s+(\{[A-Z0-9\-]+\})\s+')



class Verse:
    def __init__(self, verse_lines, bookname, booknumber, encoding):
        self.chapter = self.verse = 0
        self.bookname = bookname
        self.booknumber = booknumber
        self.encoding = encoding
        self.first_monad = 0
        self.last_monad = 0
        self.current_monad = 0
        self.verse_lines = verse_lines
        self.variant = variant_none
        self.variant_first_monad = 0
        self.words = []

    def getWords(self):
        return self.words

    def parse_chapter_verse(self, cv):
        if cv[0] == "[":
            if self.bookname == "Mark":
                self.chapter = 16
                self.verse = 9
            else:
                raise Exception("Verse.parse_chapter_verse: Unknown bookname: " + self.bookname)
        else:
            chap_ver_arr = cv.split(":")
            self.chapter = chap_ver_arr[0]
            self.verse = chap_ver_arr[1]

    def parse(self, first_monad):
        # Set member variables
        self.first_monad = self.last_monad = first_monad
        self.current_monad = first_monad

        overall_line = "\n".join(self.verse_lines)

        line_words = overall_line.split()
	
        # Parse chapter/verse
        try:
            self.parse_chapter_verse(line_words[0])
        except:
            print 
            raise Exception("Error parsing verse, first element of: '%s'" % line_words)

        # If this is, e.g., the shorter ending of Mark,
        # start at index 0. Otherwise, start at index 1
        if line_words[0][0] == "[":
            index = 0
        else:
            index = 1

        # Strip parens-words.
        # This is things like "(26-61)", indicating that NA27
        # starts the verse here.
        line_word_candidates = []
        for w in line_words[index:]:
            kind = recognize(w)
            if kind == kind_unknown:
                raise Exception("Error in Verse.parse: Unknown word kind: '" + w + "'")
            else:
                line_word_candidates.append(w)

        # Parse rest of words
        self.parse_words(line_word_candidates)

        if self.last_monad < first_monad:
            print "Error in verse: ", self.bookname, self.chapter, self.verse

        return self.last_monad

    def parse_words(self, words):
        index = 0
        while index < len(words):
            w = Word(self.current_monad, self.encoding)
            index = w.parse(index, words)
            self.words.append(w)
            self.current_monad += 1


    def writeWordsMQL(self, f, bUseOldStyle):
        for w in self.words:
            w.writeMQL(f, bUseOldStyle)

    def writeMQL(self, f, bUseOldStyle):
        print >>f, "CREATE OBJECT"
        print >>f, "FROM MONADS={" + str(self.first_monad) + "-" + str(self.last_monad) + "}"
        if bUseOldStyle:
            OT = "Verse"
        else:
            OT = ""
        print >>f, "[%s" % OT
        print >>f, "  book:=" + self.bookname + ";"
        print >>f, "  chapter:=" + str(self.chapter) + ";"
        print >>f, "  verse:=" + str(self.verse) + ";"
        print >>f, "]"
        if bUseOldStyle:
            print >>f, "GO"
        print >>f, ""

    def writeSFM(self, f, cur_monad):
        word_index = 1
        for w in self.words:
            w.writeSFM(f, self.booknumber, self.chapter, self.verse, word_index, cur_monad)
            word_index += 1
            cur_monad += 1
        return cur_monad

    def getRef(self):
        return "%s %s:%s" % (self.bookname, str(self.chapter), str(self.verse))

    def get_MORPH_ref(self, verse_copy, bDoVerseCopy = True):
        if verse_copy != "" and bDoVerseCopy:
            base_ref = "%s %d:%d.%s" % (reader.book_list_OLB[self.booknumber-1], int(self.chapter), int(self.verse), verse_copy)
        else:
            base_ref = "%s %d:%d" % (reader.book_list_OLB[self.booknumber-1], int(self.chapter), int(self.verse))
        return base_ref
        
    def write_MORPH_style(self, f, verse_copy, encodingStyle):
        base_ref = self.get_MORPH_ref(verse_copy, False)
        index = 1
        for w in self.words:
            w.write_MORPH_style(f, base_ref, index, True, encodingStyle)
            index += 1

    def write_subset_MORPH_style(self, f, verse_copy, word_predicate, manualanalyses, encodingStyle):
        base_ref = self.get_MORPH_ref(verse_copy)
        index = 1
        for w in self.words:
            thisref = "%s.%d" % (base_ref, index)
            if manualanalyses.getTuple(thisref) <> None or word_predicate(w):
                w.write_MORPH_style(f, base_ref, index, False, encodingStyle)
            index += 1

    def write_StrippedLinear(self, f, verse_copy):
        base_ref = self.get_MORPH_ref(verse_copy)
        index = 1
        for w in self.words:
            w.write_StrippedLinear(f, base_ref, index)
            index += 1

    def write_WHLinear(self, f, verse_copy):
        base_ref = self.get_MORPH_ref(verse_copy)
        index = 1
        for w in self.words:
            w.write_WHLinear(f, base_ref, index)
            index += 1

    def write_Linear(self, f, verse_copy):
        base_ref = self.get_MORPH_ref(verse_copy)
        index = 1
        for w in self.words:
            w.write_Linear(f, base_ref, index)
            index += 1

    def apply_predicate(self, OLB_bookname, pred, extra):
	for w in self.words:
	    pred(OLB_bookname, self.chapter, self.verse, w, extra)

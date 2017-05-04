# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals, print_function

import sys
import string
import re

import booknames
from word import *
from variant import *
from kind import *
import readwhat

 

 
text_variant_strongs_parsing_re= re.compile(r'\|\s+([a-z\[\]<>]+)\s+\|\s+([a-z\[\]<>]+)\s+\|([0-9\s]+\{[A-Z0-9\-]+\})\s*')

text_strongs_varparsing_varparsing_re = re.compile(r'(\s+[a-z\[\]<>]+\s+[0-9]+\s+)\|\s+(\{[A-Z0-9\-]+\})\s+\|\s+(\{[A-Z0-9\-]+\})\s+\|')

text_strongs_vartext_varstrongs_parsing = re.compile(r'\|\s+([a-z\[\]<>]+\s+[0-9]+)\s+\|\s+([a-z\[\]<>]+\s+[0-9]+)\s+\|\s+(\{[A-Z0-9\-]+\})\s+')

text_zerostrongs_re = re.compile(r'\s+0\s+([0-9]+)')

text_variant_strongs_parsing_variant_strongs_parsing = re.compile(r'([a-z\[\]<>]+)\s+\|\s+([0-9]+\s+\{[A-Z0-9\-]+\})\s+\|\s+([0-9]+\s+\{[A-Z0-9\-]+\})\s+\|')

text_strongs_variant_strongs_parsing_variant_strongs_parsing = re.compile(r'([a-z\[\]<>]+\s+[0-9]+)\s+\|\s+([0-9]+\s+\{[A-Z0-9\-]+\})\s+\|\s+([0-9]+\s+\{[A-Z0-9\-]+\})\s+\|')

text_strongs_variant_text_strongs_strongs_variant_parsing = re.compile(r'\|\s+([a-z\[\]<>]+\s+[0-9]+)\s+\|\s+([a-z\[\]<>]+\s+[0-9]+\s+[0-9]+)\s+\|\s+(\{[A-Z0-9\-]+\})\s+')

class Verse:
    def __init__(self, verse_lines, bookname, booknumber):
        self.chapter = self.verse = 0
        self.bookname = bookname
        self.booknumber = booknumber
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
        #print("UP20: " + self.bookname + " " + cv)
        if cv[0] == "[":
            if self.bookname == "Mark":
                self.chapter = 16
                self.verse = 9
            else:
                raise Exception("Verse.parse_chapter_verse: Unknown bookname: " + self.bookname)
        else:
            chap_ver_arr = cv.split(":")
            self.chapter = int(chap_ver_arr[0])
            self.verse = int(chap_ver_arr[1])
            #print("%s:%s" % (self.chapter, self.verse))

        
    def encode_word(self, word):
        result = '"'
        for c in word:
            if c == '"':
                result = result + '\\"'
            elif c == "\\":
                result = result + "\\\\"
            else:
                result = result + c
        result += '"'
        return result

    def parse(self, first_monad, read_what):
        # Set member variables
        self.first_monad = self.last_monad = first_monad
        self.current_monad = first_monad

        # Concatenate all lines
        overall_line = " ".join(self.verse_lines)
        #print(overall_line)

        # Get rid of Zero Strong's
        if text_zerostrongs_re.search(overall_line) != None:
            overall_line = text_zerostrongs_re.sub(r' 0\1 ', overall_line)

        if text_variant_strongs_parsing_re.search(overall_line) != None:
            overall_line = text_variant_strongs_parsing_re.sub(r'| \1 \3 | \2 \3 | ', overall_line)

        if text_strongs_varparsing_varparsing_re.search(overall_line) != None:
            overall_line = text_strongs_varparsing_varparsing_re.sub(r'| \1 \2 | \1 \3 | ', overall_line)

        if text_strongs_vartext_varstrongs_parsing.search(overall_line) != None:
            overall_line = text_strongs_vartext_varstrongs_parsing.sub(r'| \1 \3 | \2 \3 | ', overall_line)
            
        if text_variant_strongs_parsing_variant_strongs_parsing.search(overall_line) != None:
            overall_line = text_variant_strongs_parsing_variant_strongs_parsing.sub(r'| \1 \2 | \1 \3 | ', overall_line)

        if text_strongs_variant_strongs_parsing_variant_strongs_parsing.search(overall_line) != None:
            overall_line = text_strongs_variant_strongs_parsing_variant_strongs_parsing.sub(r'| \1 \2 | \1 \3 | ', overall_line)

        if text_strongs_variant_text_strongs_strongs_variant_parsing.search(overall_line) != None:
            sys.stderr.write("UP202!\n")
            overall_line = text_strongs_variant_text_strongs_strongs_variant_parsing.sub(r'| \1 \3 | \2 \3 | ', overall_line)
            
            



        # In Romans 16:27, we find the line ends with "{HEB}|".
        # We need this to be "{HEB} |".
        overall_line = overall_line.replace("}|", "} |")

        # Split into words
        line_words = overall_line.split()

        # Parse chapter/verse
        try:
            self.parse_chapter_verse(line_words[0])
        except:
            print(overall_line)
            raise Exception("Error...")

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
            elif kind == kind_parens:
                pass
            else:
                line_word_candidates.append(w)

        # Parse rest of words
        self.parse_words(line_word_candidates, read_what)

        #print("len(self.words) = %d, last_monad - first_monad = %d" % (len(self.words), self.last_monad - self.first_monad))

        if self.last_monad < first_monad:
            print("Error in verse: ", self.bookname, self.chapter, self.verse)

        return self.last_monad

    def parse_words(self, words, read_what):
        index = 0
        while index < len(words):
            if words[index] == "|":
                if self.variant == variant_none:
                    self.variant = variant_first
                    self.variant_first_monad = self.current_monad
                    self.first_variant_monad_offset = 0
                elif self.variant == variant_first:
                    self.variant = variant_second
                    self.second_variant_monad_offset = 0
                elif self.variant == variant_second:
                    self.variant = variant_none
                    if read_what == readwhat.read_wh_only:
                        self.current_monad = self.variant_first_monad + self.first_variant_monad_offset
                    elif read_what == readwhat.read_na27_only:
                        self.current_monad = self.variant_first_monad + self.second_variant_monad_offset
                    else: # Read both na27 and WH
                        #print("UP2")
                        self.current_monad = self.variant_first_monad + max(self.first_variant_monad_offset, self.second_variant_monad_offset)
                    self.last_monad = self.current_monad
                else:
                    raise Exception("Error: Unknown self.variant")
                index = index+1
            else:
                word_monad = 0
                if self.variant == variant_none:
                    word_monad = self.current_monad
                    self.last_monad = self.current_monad
                    self.current_monad += 1
                elif self.variant == variant_first:
                    word_monad = self.variant_first_monad + self.first_variant_monad_offset
                    self.first_variant_monad_offset += 1
                elif self.variant == variant_second:
                    word_monad = self.variant_first_monad + self.second_variant_monad_offset
                    self.second_variant_monad_offset += 1
                else:
                    raise Exception("Error: Unknown self.variant")
                w = Word(word_monad, self.variant)
                index = w.parse(index, words)
                if read_what == readwhat.read_wh_only:
                    if self.variant == variant_none or self.variant == variant_first:
                        self.words.append(w)
                elif read_what == readwhat.read_na27_only:
                    if self.variant == variant_none or self.variant == variant_second:
                        self.words.append(w)
                elif read_what in [readwhat.read_wh_and_na27]:
                    self.words.append(w)
                else:
                    raise Exception("Unknown read_what:" + str(read_what))

    def writeWordsMQL(self, f, bUseOldStyle):
        #print("UP280: %s" % self.getRef())
        for w in self.words:
            w.writeMQL(f, bUseOldStyle)

    def writeMQL(self, f, bUseOldStyle):
        print("CREATE OBJECT", file=f)
        print("FROM MONADS={" + str(self.first_monad) + "-" + str(self.last_monad) + "}", file=f)
        if bUseOldStyle:
            OT = "Verse"
        else:
            OT = ""
        print("[%s" % OT, file=f)
        print("  book:=" + self.bookname + ";", file=f)
        print("  chapter:=" + str(self.chapter) + ";", file=f)
        print("  verse:=" + str(self.verse) + ";", file=f)
        print("]", file=f)
        if bUseOldStyle:
            print("GO", file=f)
        print("", file=f)

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
            base_ref = "%s %d:%d.%s" % (booknames.book_lists["OLB"][self.booknumber-1], int(self.chapter), int(self.verse), verse_copy)
        else:
            base_ref = "%s %d:%d" % (booknames.book_lists["OLB"][self.booknumber-1], int(self.chapter), int(self.verse))
        return base_ref
        
    def write_MORPH_style(self, f, verse_copy, encodingStyle):
        base_ref = self.get_MORPH_ref(verse_copy, False)
        index = 1
        for w in self.words:
            w.write_MORPH_style(f, base_ref, index, encodingStyle)
            index += 1

    def write_subset_MORPH_style(self, f, verse_copy, word_predicate, manualanalyses, encodingStyle):
        base_ref = self.get_MORPH_ref(verse_copy)
        index = 1
        for w in self.words:
            thisref = "%s.%d" % (base_ref, index)
            #thisref = "%s" % (base_ref, index)            
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

            

# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals, print_function

import os
import sys, codecs, locale

from book import Book
from readwhat import *
from kind import *
from word import *


def read_WH(read_what):
    if read_what == read_na27_only:
        return False
    else:
        return True

def read_NA27(read_what):
    if read_what == read_wh_only:
        return False
    else:
        return True

MY_PATH = os.path.abspath(os.path.dirname(__file__))


class Reader:
    def __init__(self, directory, suffix):
        self.current_monad = 1
        self.suffix = suffix
        self.directory = directory
        self.books = []

    def open_wb_file(self, infilename):
        f = open(infilename, "wb")
        return codecs.getwriter('utf-8')(f)

    def read_NT(self, read_what):
        for bkname in booknames.book_lists["OLB"]:
            self.read_book(bkname, read_what)

    def read_book(self, bookname, read_what):
        if self.suffix == "":
            print(bookname)
            filename = os.path.join(self.directory, bookname)
        else:
            basename = "%s.%s" % (bookname, self.suffix)
            print(basename)
            filename = os.path.join(self.directory, basename)
        book = Book(filename)
        self.books.append(book)
        self.current_monad = book.read(self.current_monad, read_what) + 1

            
    def parse_sentences(self):
        for index in range(0,27):
            self.books[index].parse_sentences()
            
    def write_SFM(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            gdb_bookname = booknames.book_lists["UBS"][index]
            outfilename = os.path.join(outdir, "%s.%s" % (gdb_bookname, suffix))
            cur_monad = self.writeBookAsSFM(outfilename, self.books[index], cur_monad)

    def writeBookAsSFM(self, filename, book, cur_monad):
        f = self.open_wb_file(filename)
        cur_monad = book.writeSFM(f, cur_monad)
        f.close()
        return cur_monad

    def write_MORPH(self, outdir, suffix):
        for index in range(0,27):
            olb_bookname = booknames.book_lists["OLB"][index]
            outfilename = os.path.join(outdir, "%s.%s" % (olb_bookname, suffix))
            cur_monad = self.write_book_MORPH_style(index, outfilename, kUnicode)

    def write_StrippedLinear(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            olb_bookname = booknames.book_lists["OLB"][index]
            outfilename = os.path.join(outdir, "%s.%s" % (olb_bookname, suffix))
            fout = self.open_wb_file(outfilename)
            self.books[index].write_StrippedLinear(fout)
            fout.close()

    def write_WHLinear(self, outfilename):
        cur_monad = 1
        f = self.open_wb_file(outfilename)
        for index in range(0,27):
            self.books[index].write_WHLinear(f)
        f.close()

    def write_Linear(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            olb_bookname = booknames.book_lists["OLB"][index]
            outfilename = os.path.join(outdir, "%s.%s" % (olb_bookname, suffix))
            self.books[index].write_Linear(outfilename)

    def write_MQL(self, mqlfilename, bUseOldStyle):
        """Write an Emdros MQL script to create an Emdros database.
Emdros is a text database engine or digital library platform.
http://emdros.org/
"""
        fout = self.open_wb_file(mqlfilename)
        for index in range(0,27):
            self.books[index].writeMQL(fout, bUseOldStyle)
        fout.close()


    def write_book_MORPH_style(self, index, outfilename, encodingStyle):
        fout = self.open_wb_file(outfilename)
        if index < len(self.books):
            book = self.books[index]
            book.write_MORPH_style_to_file(fout, encodingStyle)
        fout.close()
        
    def getBook(self, index):
        return self.books[index]

    def addVersesToVerseDicts(self):
        for index in range(0, len(self.books)):
            whbook = self.books[index]
            whbook.addVersesToVerseDict()


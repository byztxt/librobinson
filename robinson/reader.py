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
import book
from kind import *
from word import *
from booknames import *

read_first_variant_only = 0
read_second_variant_only = 1

# Old OLB encoding
read_OLB_encoding = 0
# with updates from MAR after 2013-08-02.
read_UMAR_encoding = 1

book_list_OLB = ["MT", "MR", "LU", "JOH", "AC", "RO", "1CO", "2CO",
                 "GA", "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI",
                 "TIT", "PHM", "HEB", "JAS", "1PE", "2PE", "1JO", "2JO", "3JO",
                 "JUDE", "RE"]



class Reader:
    def __init__(self, indir, suffix):
        self.current_monad = 1
        self.suffix = suffix
        self.indir = indir
        self.books = []
        self.lexicon = None
        self.encoding = read_OLB_encoding # default

    def read_NT(self, read_what, encoding):
        self.encoding = encoding
        for bkname in book_list("OLB"):
            self.read_book(bkname, read_what)

    def read_MT(self, read_what):
        self.encoding = encoding
	self.read_book('MT', read_what)

    def write_SFM(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            gdb_bookname = book_list("UBS")[index]
            cur_monad = self.writeBookAsSFM(os.path.join(outdir, "%s.%s" % (gdb_bookname, suffix)), self.books[index], cur_monad)

    def writeBookAsSFM(self, filename, book, cur_monad):
        f = open(filename, "w")
        cur_monad = book.writeSFM(f, cur_monad)
        f.close()
        return cur_monad

    def write_TUP(self):
        for index in range(0,27):
            olb_bookname = book_list("OLB")[index]
            cur_monad = self.write_book_MORPH_style(index, olb_bookname, "./", "TUP", kUnicode)

    def write_StrippedLinear(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            olb_bookname = book_list("OLB")[index]
            outfilename = "%s.%s" % (olb_bookname, suffix)
            outpath = os.path.join(outdir, outfilename)
            self.books[index].write_StrippedLinear(outpath)

    def write_WHLinear(self, outfilename):
        cur_monad = 1
        f = open(outfilename, "w")
        for index in range(0,27):
            self.books[index].write_WHLinear(f)
        f.close()

    def write_Linear(self, outdir, suffix):
        cur_monad = 1
        for index in range(0,27):
            olb_bookname = book_list("OLB")[index]
            outfilename = "%s.%s" % (olb_bookname, suffix)
            outpath = os.path.join(outdir, outfilename)
            self.books[index].write_Linear(outpath)

    def write_MQL(self, mqlfilename, bUseOldStyle):
        fout = open(mqlfilename, "w")
        for index in range(0,27):
            self.books[index].writeMQL(fout, bUseOldStyle)
        fout.close()

    def read_book(self, bookname, read_what):
        if self.suffix == "":
            print(bookname)
            filename = self.indir + "/" + bookname
        else:
            print(bookname + "." + self.suffix)
            filename = self.indir + "/" + bookname + "." + self.suffix
        this_book = book.Book(filename, self.encoding)
        self.books.append(this_book)
        self.current_monad = this_book.read(self.current_monad, read_what)

    def writeBooks_MORPH_style(self, output_dir, output_suffix, encodingStyle):
        for index in range(0,27):
            olb_bookname = book_list("OLB")[index]
            self.write_book_MORPH_style(index, olb_bookname, output_dir, output_suffix, encodingStyle)

    def writeSubset_MORPH_style(self, filename, word_predicate, manualanalyses, encodingStyle):
        f = open(filename, "w")
        for index in range(0,27):
            olb_bookname = book_list("OLB")[index]
            self.write_subset_MORPH_style(f, index, word_predicate, manualanalyses, encodingStyle)
        f.close()

    def write_book_MORPH_style(self, index, bookname, output_dir, output_suffix, encodingStyle):
        if output_suffix == "":
            print(bookname)
            filename = output_dir + "/" + bookname
        else:
            print(bookname + "." + output_suffix)
            filename = output_dir + "/" + bookname + "." + output_suffix
        this_book = self.books[index]
        this_book.write_MORPH_style(filename, encodingStyle)
        
    def write_subset_MORPH_style(self, f, index, word_predicate, manualanalyses, encodingStyle):
        this_book = self.books[index]
        this_book.write_subset_MORPH_style(f, word_predicate, manualanalyses, encodingStyle)

    def getBook(self, index):
        return self.books[index]

    def addVersesToVerseDicts(self):
        for index in range(0, len(self.books)):
            whbook = self.books[index]
            whbook.addVersesToVerseDict()

    # pred must take four parameters:
    # (OLB_bookname, chapternumber, versenumber, word, extra)
    def apply_predicate(self, pred, extra):
	for index in range(0, len(self.books)):
	    mybook = self.books[index]
	    mybook.apply_predicate(pred, extra)

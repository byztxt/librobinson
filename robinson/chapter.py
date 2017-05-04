# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals, print_function

class Chapter:
    def __init__(self, first_monad, last_monad, chapter, bookname):
        self.first_monad = first_monad
        self.last_monad = last_monad
        self.chapter = chapter
        self.bookname = bookname

    def writeMQL(self, f, bUseOldStyle):
        print("CREATE OBJECT", file=f)
        print("FROM MONADS={" + str(self.first_monad) + "-" + str(self.last_monad) + "}", file=f)
        if bUseOldStyle:
            OT = "Chapter"
        else:
            OT = ""
        print("[%s" % OT, file=f)
        print("  book:=" + self.bookname + ";", file=f)
        print("  chapter:=" + str(self.chapter) + ";", file=f)
        print("]" , file=f)
        if bUseOldStyle:
            print("GO", file=f)
        print("", file=f)


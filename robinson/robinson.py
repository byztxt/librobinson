# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals
import os
import sys
import reader
import readwhat


def read_robinson(directory, suffix, read_what):
    read_what = readwhat.normalize(read_what)
    read_what_str = readwhat.read_what2string(read_what)
    sys.stderr.write("Now reading '%s' from directory %s with suffix %s\n" % (read_what_str, directory, suffix))
    rd = reader.Reader(directory, suffix)
    rd.read_NT(read_what)
    return rd

def test():
    indirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'WHP'))
    suffix = "WHP"

    readers = []
    
    #for read_what in ["text_only", "variants_only", "text_and_variants"]:
    for read_what in ["text_only"]:
        rd = read_robinson(indirectory, suffix, read_what)
        readers.append((read_what, rd))

    outdir = "/tmp"
        
    for (read_what, rd) in readers:
        for (write_what, basename, suffix) in [
                ("SFM", "", "SFM"),
                ("MORPH", "", "MRP"), 
                ("StrippedLinear", "", "SLN"),
                ("Linear", "", "LIN"),
                ("WHLinear", "WHLinear.txt", ""),
                ("MQLOldStyle", "blah1.mql", ""),
                ("MQLNewStyle", "blah2.mql", "")
       ]:
            print("Now writing %s of %s" % (write_what, read_what))
            if write_what == "MQLOldStyle":
                function = "rd.write_MQL(basename, True)"
            elif write_what == "MQLNewStyle":
                function = "rd.write_MQL(basename, False)"
            elif basename == "":
                function = "rd.write_%s(outdir, suffix)" % write_what
            elif suffix == "":
                function = "rd.write_%s(basename)" % write_what
            else:
                raise Exception("write_what %s not yet implemented." % write_what)
                
            eval(function)

            
    

if __name__ == '__main__':
    test()

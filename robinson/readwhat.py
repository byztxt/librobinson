# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals

read_wh_only = 0
read_wh_and_na27 = 1
read_na27_only = 2

read_what_dict = {
    "text_only" : read_wh_only,
    "text_and_variants" : read_wh_and_na27,
    "variants_only" : read_na27_only,
    }

read_what_int_list = [item[1] for item in read_what_dict.items()]

read_what_string_list = list(sorted(read_what_dict.keys()))

def normalize(readwhat):
    if readwhat in read_what_int_list:
        return read_what
    elif readwhat in read_what_dict:
        return read_what_dict[readwhat]
    raise Exception("Error: unknown readwhat %s in read_what.normalize()\nShould be one of: %s" % (str(readwhat), str(read_what_string_list)))


def read_what2string(read_what):
    if read_what in read_what_int_list:
        read_what2 = read_what
    else:
        read_what2 = normalize(read_what)

    for key in read_what_dict:
        value = read_what_dict[key]
        if value == read_what2:
            return key

    raise Exception("Error: Unknown readwhat %s" % str(read_what))


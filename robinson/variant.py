# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
variant_none = 0
variant_first = 1
variant_second = 2

def variant2string(v):
    if v == variant_none:
        return "none"
    elif v == variant_first:
        return "var_first"
    elif v == variant_second:
        return "var_second"
    else:
        raise Exception("Error: variant unknown in variant2string(%s)" % str(v))


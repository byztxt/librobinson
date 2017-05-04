# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#


from __future__ import unicode_literals, print_function

import sys
import pprint
import copy


part_dict = {
    "case" : {
        "V" : "vocative",
        "N" : "nominative",
        "A" : "accusative",
        "D" : "dative",
        "G" : "genitive",
    },
    "case_possessed" : {
        "V" : "vocative",
        "N" : "nominative",
        "A" : "accusative",
        "D" : "dative",
        "G" : "genitive",
    },
    "gender" : {
        "M" : "masculine",
        "F" : "feminine",
        "N" : "neuter",
    },
    "gender_possessed" : {
        "M" : "masculine",
        "F" : "feminine",
        "N" : "neuter",
    },
    "number" : {
        "S" : "singular",
        "P" : "plural",
    },
    "number_possessed" : {
        "S" : "singular",
        "P" : "plural",
    },
    "number_possessor" : {
        "S" : "singular",
        "P" : "plural",
    },
    "person" : {
        "1" : "1st",
        "2" : "2nd",
        "3" : "3rd",
        },
    "person_possessor" : {
        "1" : "1st",
        "2" : "2nd",
        "3" : "3rd",
        },
    "person_possessed" : {
        "1" : "1st",
        "2" : "2nd",
        "3" : "3rd",
        },
    "tense" : {
        "P"  : "present",
        "I"  : "imperfect",
        "F"  : "future",
        "2F" : "second future",
        "A"  : "aorist",
        "2A" : "second aorist",
        "R"  : "perfect",
        "2R" : "second perfect",
        "L"  : "pluperfect",
        "2L" : "second pluperfect",
        "X"  : "no tense stated",
    },
    "voice" : {
        "A" : "active",
        "M" : "middle",
        "P" : "passive",
        "E" : "middle or passive",
        "D" : "middle deponent",
        "O" : "passive deponent",
        "N" : "middle or passive deponent",
        "Q" : "impersonal active",
        "X" : "no voice",
    },
    "mood" : {
        "I-" : "indicative",
        "S-" : "subjunctive",
        "O-" : "optative",
        "M-" : "imperative",
        "N" : "infinitive",
        "P-" : "participle",
        "R-" : "imperative participle",
    },
    "verb-extra" : {
        "-M"   : "middle significance",
        "-C"   : "contracted form",
        "-T"   : "transitive",
        "-A"   : "aeolic",
        "-ATT" : "attic",
        "-AP"  : "apocopated form",
        "-IRR" : "irregular or impure form",
    },
    "suffix" : {
        "-S"   : "superlative",
        "-C"   : "comparative",
        "-ABB" : "abbreviated",
        "-I"   : "interrogative",
        "-N"   : "negative",
        "-ATT" : "attic",
        "-P"   : "particle attached",
        "-K"   : "crasis",
        "-INDECL" : "indeclinable",
        "-CONDITIONAL" : "conditional",
    },
}

pos_dict = {
    # NON-STANDARD Robinson tags
    "PUNCT" : [
    ],

    # STANDARD Robinson tags
    "ADV" : [
        "opt_suffix",
    ],
    "CONJ" : [
        "opt_suffix",
    ],
    "COND" : [
        "opt_suffix",
    ],
    "PRT" : [
        "opt_suffix",
    ],
    "PREP" : [
        "opt_suffix",
    ],
    "POSTP" : [
        "opt_suffix",
    ],
    "INJ" : [
        "opt_suffix",
    ],
    "ARAM" : [
        "opt_suffix",
    ],
    "HEB" : [
        "opt_suffix",
    ],
    "N-PRI" : [
        "opt_suffix",
    ],
    "A-NUI" : [
        "opt_suffix",
    ],
    "N-LI" : [
        "opt_suffix",
    ],
    "N-OI" : [
        "opt_suffix",
    ],
    "N-" : [
        "case",
        "number",
        "gender",
        "opt_suffix",
    ],
    "NPROP-" : [
        "case",
        "number",
        "gender",
        "opt_suffix",
    ],
    "A-" : [ 
        "case",
        "number",
        "gender",
        "opt_suffix",
    ],
    "T-" : [
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "V-" : [
        "tense",
        "voice",
        "mood",
        "opt_person",
        "opt_case",
        "opt_number",
        "opt_gender",
        "opt_verb-extra",
        ],
    "P-" : [
        "opt_person",
        "case",
        "number",
        "opt_gender",
        "opt_suffix",
        ],
    "R-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "C-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "D-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "K-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "I-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "X-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "Q-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "F-" : [
        "opt_person",
        "case",
        "number",
        "gender",
        "opt_suffix",
        ],
    "S-" : [
        "person_possessor",
        "number_possessor",
        "case_possessed",
        "number_possessed",
        "gender_possessed",
        ],
    
}

pos_list = [
    "ADV",
    "CONJ",
    "COND",
    "PRT",
    "PREP",
    "POSTP",
    "INJ",
    "ARAM",
    "HEB",
    "N-PRI",
    "A-NUI",
    "N-LI",
    "N-OI",
    "N-",
    "NPROP-",
    "A-",
    "T-",
    "V-",
    "P-",
    "R-",
    "C-",
    "D-",
    "K-",
    "I-",
    "X-",
    "Q-",
    "F-",
    "S-",
    "PUNCT", # NON-STANDARD
    ]


def decode_robinson_tag(tag):
    result = {}

    for pos in pos_list:
        if len(tag) >= len(pos) and tag[0:len(pos)] == pos:
            result["pos"] = pos
            index = len(pos)
            for part in pos_dict[pos]:
                if len(part) > 4 and part[0:4] == "opt_":
                    bIsOpt = True
                    real_part = part[4:]
                else:
                    bIsOpt = False
                    real_part = part
                    
                bFound = False
                for instr in part_dict[real_part]:
                    if len(tag) >= index + len(instr) \
                       and tag[index:index+len(instr)] == instr:
                        translation = part_dict[real_part][instr]
                        result[part] = translation
                        bFound = True
                        break
                if bFound:
                    index += len(instr)
                elif bIsOpt:
                    result[part] = "NA"
                    
            break

    return result

def encode_robinson_tag(tagdict):
    pos = tagdict["pos"]
    tag_list = [pos]
    for part in pos_dict[pos]:
        if len(part) > 4 and part[0:4] == "opt_":
            bIsOpt = True
            real_part = part[4:]
        else:
            bIsOpt = False
            real_part = part

        real_value = tagdict[part]
        if bIsOpt and real_value == "NA":
            pass
        else:
            for outstr in part_dict[real_part]:
                value = part_dict[real_part][outstr]
                if value == real_value:
                    tag_list.append(outstr)
                    break

    return "".join(tag_list)






def test_tag(tag):
    r = decode_robinson_tag(tag)
    pprint.pprint(r)
    outtag = encode_robinson_tag(r)
    if outtag == tag:
        print("SUCCESS: tag == outtag: %s == %s" % (tag, outtag))
        return True
    else:
        print("FAILURE: tag != outtag: '%s' != '%s'" % (tag, outtag))
        return False
        
def test_module():
    bResult = True
    bResult = bResult and test_tag("T-NSF")
    bResult = bResult and test_tag("N-LI")
    bResult = bResult and test_tag("N-OI")
    bResult = bResult and test_tag("V-AAI-3S")
    bResult = bResult and test_tag("ADV-K")
    bResult = bResult and test_tag("HEB-ABB")
    bResult = bResult and test_tag("V-AAP-GSF-ATT")
    bResult = bResult and test_tag("V-2AMP-NSM")
    bResult = bResult and test_tag("V-2AMP-NSM")
    bResult = bResult and test_tag("V-2AER-APN")
    bResult = bResult and test_tag("V-2LAI-2P")

    print("")
    
    if bResult:
        print("SUCCESS: All tests passed.")
    else:
        print("FAILURE: At least one test failed.")

    return bResult

if __name__ == '__main__':
    test_module()
    

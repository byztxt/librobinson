# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2017 Scripture Systems ApS
#
# Made available under the MIT License.
#
# See the file LICENSE in the distribution for details.
#
from __future__ import unicode_literals, print_function

import string
from variant import *
from kind import *
import re
import convert
import booknames
import unicodedata

#state_surface = 0
#state_strongs1 = 1
#state_strongs2 = 2
#state_parsing = 3

state_none = 0
state_surface = 1
state_strongs1 = 2
state_strongs2 = 3
state_strongs3 = 4
state_parsing = 5
state_alt_strongs1 = 6
state_alt_strongs2 = 7
state_alt_strongs3 = 8
state_alt_parsing = 9


def mangleMQLString(str):
    return str.replace("\\", "\\\\").replace("\"", "\\\"")


class Word:
    def __init__(self, monad, variant):
        self.monad = monad
        self.break_kind = "."   # Can be 'C' for chapter-break, 'P' for paragraph-break, or '.' for no break.
        self.surface = ""       # kethiv (i.e., it is written (in the printed version))
        self.qere = ""          # qere (i.e., please read)
        self.qere_noaccents = ""
        self.accented_surface = ""
        self.parsing = ""
        self.alt_parsing = ""
        self.Strongs1 = -1
        self.Strongs2 = -1
        self.Strongs1_has_zero = False
        self.alt_Strongs1 = -1
        self.alt_Strongs2 = -1
        self.variant = variant
        self.tag_object = None

    def has_qere_noaccents(self):
        return self.qere_noaccents != ""

    def ends_sentence(self):
	return self.accented_surface[-1] in [".", ";"]

    def isVariant(self):
        return self.variant == variant_second or self.variant == variant_none

    def getStrongs(self):
        lemma = ""
        if self.Strongs1 != -1:
            lemma += str(self.Strongs1)
        if self.Strongs2 != -1:
            lemma += "&" + str(self.Strongs2)
        return lemma

    def getAltStrongs(self):
        lemma = ""
        if self.alt_Strongs1 != -1:
            lemma += str(self.alt_Strongs1)
        if self.alt_Strongs2 != -1:
            lemma += "&" + str(self.alt_Strongs2)
        return lemma

    def setStrongs(self, strongs):
        if "&" in strongs:
            mylist = strongs.split("&")
            self.Strongs1 = int(mylist[0])
            self.Strongs2 = int(mylist[1])
        elif "/" in strongs:
            self.Strongs1 = strongs
        else:
            self.Strongs1 = int(strongs)



    def writeSFM(self, f, booknumber, chapter, verse, word_index, monad):
        print((self.getSFMReference(f, booknumber, chapter, verse, word_index) + ""), file=f)
        if self.accented_surface != "":
            surfaceUTF8 = self.accented_surface
        else:
            surfaceUTF8 = self.beta2utf8(convert.OLBtoBETAtranslate(self.surface))
        print("\\text %s" % surfaceUTF8, file=f)
        print("\\trans %s %d:%d" % (booknames.book_lists["UBS"][booknumber-1], chapter, verse), file=f)
        if len(self.parsing) > 0:
            print("\\pars %s" % self.parsing, file=f)
        print("\\monad %d" % monad, file=f)
        print("\\strongs %s" % self.getStrongs(), file=f)
        print("\\re", file=f)
        print("", file=f)

    def beta2galatia(self, beta):
        result = ""
        for s in beta.split(" "):
            # Add '\n' at the end to convert final sigma to real final sigma.
            # The '\n' will be stripped out by the conversion
            galatia, remainder = convert.beta2galatiatrie.convert(s+"\n")
            if remainder != "":
                raise Exception("galatia = '" + galatia +"'\nbeta = " + beta + "\n, and remainder was not empty, but was: '" + remainder + "'")
            result += galatia + " "
        return result[0:-1]

    def beta2utf8(self, beta):
        result = []
        for s in beta.split(" "):
            # Add '\n' at the end to convert final sigma to real final sigma.
            # The '\n' will be stripped out by the conversion
            ustr = convert.beta2unicode(s)

            #print(("'%s' --> '%s'" % (s, ustr)))

            result.append(ustr)

        return " ".join(result)

    def getSFMReference(self, f, booknumber, chapter, verse, word_index):
        return "\\rf %02d-%03d-%03d-%03d\r" % (int(booknumber), int(chapter), int(verse), int(word_index))

    def writeMQL(self, f, bUseOldStyle):
        print("CREATE OBJECT", file=f)
        print("FROM MONADS={%d}" % self.monad, file=f)
        if bUseOldStyle:
            OT = "Word"
        else:
            OT = ""
        print("[%s" % OT, file=f)

        if self.accented_surface != "":
            surfaceBETA = self.accented_surface
            qere = self.qere
        else:
            surfaceBETA = convert.OLBtoBETAtranslate(convert.stripolb(self.surface))
            qere = convert.OLBtoBETAtranslate(convert.stripolb(self.qere))
        print("  surface:=\"%s\";" % mangleMQLString(surfaceBETA), file=f)
        print("  surfaceutf8:=\"%s\";" % mangleMQLString(self.beta2utf8(surfaceBETA)), file=f)
        print("  qere:=\"%s\";" % mangleMQLString(qere), file=f)
        print("  qereutf8:=\"%s\";" % mangleMQLString(self.beta2utf8(qere)), file=f)
        print("  olb_surface:=\"%s\";" % self.surface, file=f)
        if len(self.parsing) > 0:
            print("  parsing:=\"%s\";" % self.parsing, file=f)
        if self.Strongs1 != -1:
            print("  strongs1:=%s;" % str(self.Strongs1), file=f)
        if self.Strongs2 != -1:
            print("  strongs2:=%s;" % str(self.Strongs2), file=f)
        print("]", file=f)
        if bUseOldStyle:
            print("GO\n", file=f)
        else:
            print("", file=f)

    def writeSFMShort(self, f):
        print("\\text %s" % convert.OLBtoBETAtranslate(self.surface), file=f)
        print("\\monad %s" % str(self.monad), file=f)
        if len(self.parsing) > 0:
            print("\\pars %s" % self.parsing, file=f)
        if self.Strongs1 != -1:
            print("\\str1 %d" % self.Strongs1, file=f)
        if self.Strongs2 != -1:
            print("\\str2 %d" % self.Strongs2, file=f)
        if len(self.alt_parsing) > 0:
            print("\\altpars %s" % self.alt_parsing, file=f)
        if self.alt_Strongs1 != -1:
            print("\\altstr1 %d" % self.alt_Strongs1, file=f)
        if self.alt_Strongs2 != -1:
            print("\\altstr2 %d" % self.alt_Strongs2, file=f)
        print("\re", file=f)

    def parseStrongs(self, strongs):
        """This is necessary because "[tou 3588]" occurs in Romans."""
        return strongs.replace(']', '')

    def parse(self, index, words):
	"""Parses up to the end of this word. Returns the index that points
	one after the end of the word."""

	state = state_none
	LAST_WORD = len(words) - 1
	while True:
	    if index > LAST_WORD:
		return index
	    # Advance if this is parens.
	    # This is such things as (26-61) indicating (I think)
	    # that NA27 starts the verse here (26:61).
	    elif recognize(words[index]) == kind_parens:
		index += 1
	    elif state == state_none:
		# Read surface
		if not recognize(words[index]) == kind_word:
		    raise Exception("Error in words: word[index]='%s' is not kind_word:\n%s" % (words[index], str(words[index:])))
		self.surface = words[index]

                if "&" in self.surface:
                    [self.surface, self.qere] = self.surface.split("&")
                else:
                    self.qere = self.surface
                self.qere_noaccents = convert.RemoveAccents(convert.BETAtoOLBtranslate(self.qere))
	
		# Advance index
		index += 1

		state = state_surface
	    elif state == state_surface:
		# Try next word
		kind = recognize(words[index])
		if kind == kind_number:
		    self.Strongs1 = int(self.parseStrongs(words[index]))
                    if words[index][0] == '0':
                        self.Strongs1_has_zero = True

		    state = state_strongs1
		    # In Romans, the text "[tou 3588]" occurs.
		    if self.surface[0] == '[' and words[index][-1] == ']':
			self.surface += ']'
		    if words[index][-1] == ">":
			self.surface += ">"
		    index += 1
		elif kind in [kind_pipe, kind_VAR, kind_END]:
		    return index
		elif kind == kind_word:
		    # We are not doing parsing or variant, so we have the next surface
		    return index
		else:
		    raise Exception("Error in Word.parse: 1: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")
	    elif state == state_strongs1:
		# Try next word
		kind = recognize(words[index])
		if kind == kind_number:
		    self.Strongs2 = int(self.parseStrongs(words[index]))
		    state = state_strongs2
		    index += 1
		elif kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_parsing
		    self.parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 2: Unknown kind:" + str(kind) + " '" +str(words[index]) + "' index=" + str(index) +", words = " + str(words[index:]))
	    elif state == state_strongs2:
		kind = recognize(words[index])
		
		# It should be parsing or Strongs3 at this point
		if kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_parsing
		    self.parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		elif kind == kind_number:
		    state = state_strongs3
		    self.Strongs3 = self.parseStrongs(words[index])
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 3: Unknown kind: " + str(kind) + "'" +str(words[index]) + "' " + str(words))
	    elif state == state_strongs3:
		# Try next word
		kind = recognize(words[index])
		
		# It should be parsing at this point
		if kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_parsing
		    self.parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 32: Unknown kind: " + str(kind) + "'" +str(words[index]) + "' " + str(words))
	    elif state == state_parsing:
		# So the parsing is read.  The next should either be kind_word
		# or kind_number (but may be state_parsing)

		# If we have gone past the end, return
		if len(words) <= index:
		    return index

		# Try next word
		kind = recognize(words[index])
		if kind == kind_number:
		    self.alt_Strongs1 = int(words[index])
		    state = state_alt_strongs1
		    index += 1
		elif kind == kind_word or kind in [kind_pipe, kind_VAR, kind_END, kind_parens, kind_verse]:
		    # If this is a kind_word, kind_pipe or kind_parens,
		    # we should return now.
		    # If it is a kind_word or a kind_parens, the next word will
		    # take care of it.
		    # If it is a kind_pipe, the verse will take care of it.
		    return index
		elif kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_alt_parsing
		    self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 5: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")
	    elif state == state_alt_strongs1:
		# Try next word
		kind = recognize(words[index])
		if kind == kind_number:
		    self.alt_Strongs2 = int(words[index])
		    state = state_alt_strongs2
		    index += 1
		elif kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_alt_parsing
		    self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 7: Unknown kind: " + str(kind) + " '" +str(words[index]) +"'" + "\nwords = '%s'" % words)
	    elif state == state_alt_strongs2:
		# Try next word
		kind = recognize(words[index])
		# It should be parsing or number at this point
		if kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_alt_parsing
		    self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		elif kind == kind_number:
		    self.alt_Strongs3 = int(words[index])
		    state = state_alt_strongs3
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 8: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")
	    elif state == state_alt_strongs3:
		# Try next word
		kind = recognize(words[index])
		# It should be parsing at this point
		if kind == kind_parsing:
		    if words[index][-1] != "}":
			raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
		    state = state_alt_parsing
		    self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
		    index += 1
		else:
		    raise Exception("Error in Word.parse: 9: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")
	    elif state == state_alt_parsing:
		# If we have gone past the end, return
		if len(words) <= index:
		    return index
		
		# Otherwise, the next should be a word.
		kind = recognize(words[index])
		if kind == kind_word or kind in [kind_parens, kind_pipe, kind_VAR, kind_END, kind_verse]:
		    return index
		else:
		    raise Exception("Error in Word.parse: 10: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")


    def parseOld(self, index, words):
        # Advance if this is parens.
        # This is such things as (26-61) indicating (I think)
        # that NA27 starts the verse here (26:61).

        if recognize(words[index]) == kind_parens:
            index += 1

        state = state_surface
        
        # Read surface
        if not recognize(words[index]) == kind_word:
            raise Exception("Error in words: word[index] is not kind_word:" + str(words[index:]))
        self.surface = words[index]
        if "&" in self.surface:
            [self.surface, self.qere] = self.surface.split("&")
        else:
            self.qere = self.surface
        self.qere_noaccents = convert.RemoveAccents(convert.BETAtoOLBtranslate(self.qere))


        # Advance index
        index += 1

        # If we have gone past the end, return
        if len(words) <= index:
            return index

        # Try next word
        kind = recognize(words[index])
        if kind == kind_number:
            self.Strongs1 = self.parseStrongs(words[index])
            state = state_strongs1
            index += 1

            # In Romans, the text "[tou 3588]" occurs.
            if self.surface[0] == '[' and self.Strongs1[-1] == ']':
                self.surface.append(']')
        elif kind == kind_pipe:
            return index
        elif kind == kind_word:
            # We are not doing parsing or variant, so we have the next surface
            return index
        else:
            raise Exception("Error in Word.parse: 1: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")

        # Try next word
        kind = recognize(words[index])
        if kind == kind_number:
            self.Strongs2 = self.parseStrongs(words[index])
            state = state_strongs2
            index += 1
        elif kind == kind_parsing:
            if words[index][-1] != "}":
                raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
            state = state_parsing
            self.parsing = words[index][1:-1] # Strip '{' and '}'
            index += 1
        else:
            raise Exception("Error in Word.parse: 2: Unknown kind:" + str(kind) + " '" +str(words[index]) + "', words = " + str(words))

        # If this is strongs2 state, read the parsing
        if state == state_strongs2:
            # Try next word
            kind = recognize(words[index])

            # It should be parsing at this point
            if kind == kind_parsing:
                if words[index][-1] != "}":
                    raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
                state = state_parsing
                self.parsing = words[index][1:-1] # Strip '{' and '}'
                index += 1
            else:
                raise Exception("Error in Word.parse: 3: Unknown kind: " + str(kind) + "'" +str(words[index]) + "' " + str(words))

        # So the parsing is read.  The next should either be kind_word
        # or kind_number

        # If we have gone past the end, return
        if len(words) <= index:
            return index

        # Try next word
        kind = recognize(words[index])
        if kind == kind_number:
            self.alt_Strongs1 = words[index]
            state = state_strongs1
            index += 1
        elif kind == kind_word or kind == kind_pipe or kind == kind_parens:
            # If this is a kind_word, kind_pipe or kind_parens,
            # we should return now.
            # If it is a kind_word or a kind_parens, the next word will
            # take care of it.
            # If it is a kind_pipe, the verse will take care of it.
            return index
        else:
            raise Exception("Error in Word.parse: 5: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'... words = " + " ".join(words))

        if not state == state_strongs1:
            raise Exception("Error in Word.parse: 6: Unknown state: " + str(state) + ", please correct the logic.")

        # Try next word
        kind = recognize(words[index])
        if kind == kind_number:
            self.alt_Strongs2 = words[index]
            state = state_strongs2
            index += 1
        elif kind == kind_parsing:
            if words[index][-1] != "}":
                raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
            state = state_parsing
            self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
            index += 1
        else:
            raise Exception("Error in Word.parse: 7: Unknown kind:" + str(kind) + " '" +str(words[index]) +"'")

        # If this is strongs2 state, read the parsing
        if state == state_strongs2:
            # Try next word
            kind = recognize(words[index])
            # It should be parsing at this point
            if kind == kind_parsing:
                if words[index][-1] != "}":
                    raise Exception("Error in words: parsing does not end with }: " + str(words[index:]))
                state = state_parsing
                self.alt_parsing = words[index][1:-1] # Strip '{' and '}'
                index += 1
            else:
                raise Exception("Error in Word.parse: 8: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")

        
        # If we have gone past the end, return
        if len(words) <= index:
            return index

        # Otherwise, the next should be a word.
        kind = recognize(words[index])
        if kind == kind_word or kind == kind_pipe:
            return index
        else:
            raise Exception("Error in Word.parse: 9: Unknown kind:" + str(kind) + "'" +str(words[index]) + "'")


        raise Exception("Error in Word.parse: 4: Got too far.  Please redo logic.")

            

    def toStringMQL(self):
        result = ""
        result = result + "CREATE OBJECT\n"
        result = result + "FROM MONADS={%d}" % self.monad
        result = result + "["
        result = result + "  surface:=\"%s\";\n" % convert.OLBtoBETAtranslate(self.surface)
        #result = result + "  olb_surface:=\"%s\";\n" % self.surface
        if len(self.parsing) > 0:
            result = result + "  parsing:=\"%s\";\n" % self.parsing
        if self.Strongs1 != -1:
            result = result + "  strongs1:=%s;\n" % str(self.Strongs1)
        if self.Strongs2 != -1:
            result = result + "  strongs2:=%s;\n" % str(self.Strongs2)
        #if len(self.alt_parsing) > 0:
        #    result = result + "  alt_parsing:=\"%s\";\n" % self.alt_parsing
        #if self.alt_Strongs1 != -1:
        #    result = result + "  alt_strongs1:=%s;\n" % str(self.alt_Strongs1)
        #if self.alt_Strongs2 != -1:
        #    result = result + "  alt_strongs2:=%s;\n" % str(self.alt_Strongs2)
        #if self.variant != variant_none:
        #    result = result + "  is_variant:=%s;\n" % variant2string(self.variant)
        result = result + "]"
        return result

    def toString(self):
        return "%-20s {%-15s %s}" % (self.surface, self.parsing, self.getStrongs())

    def write_MORPH_style(self, f, base_ref, index, encodingStyle):
        ref = "%s.%d" % (base_ref, index)
        #ref = "%s" % base_ref
        if self.parsing == "":
            prs = "NOPARSE"
        else:
            prs = self.parsing
        if self.Strongs1 == -1:
            strongs = "9999"
        elif self.Strongs2 == -1:
            strongs = str(self.Strongs1)
        else:
            strongs = "%s&%s" % (str(self.Strongs1), str(self.Strongs2))
        if self.Strongs1_has_zero:
            strongs = "0" + strongs

        if self.accented_surface != "":
            surf = self.accented_surface
        else:
            surf = convert.OLBtoBETAtranslate(self.surface)
        qere = convert.OLBtoBETAtranslate(self.qere)

        if encodingStyle == kBETA:
            pass
        elif encodingStyle == kUnicode:
            surf = self.beta2utf8(surf)
            qere = self.beta2utf8(qere)
        else:
            raise "Error: Unknown encodingStyle parameter = %s" % str(encodingStyle)

        print("%s %s %s %s %s %s" % (ref, self.break_kind, surf, qere, prs, strongs), file=f)

    def write_StrippedLinear(self, f, base_ref, index):
        ref = "%s" % base_ref
        print("%s %s" % (ref, convert.RemoveAccents(convert.MixedCaseBETAtoBETAtranslate(self.surface))), file=f)

    def write_WHLinear(self, f, base_ref, index):
        ref = "%s" % base_ref
        print("%s %s" % (ref, convert.OLBtoBETAtranslate(self.surface)), file=f)

    def write_Linear(self, f, base_ref, index):
        ref = "%s" % base_ref
        if self.accented_surface != "":
            surf = self.accented_surface
        else:
            surf = convert.OLBtoBETAtranslate(self.surface)
        print("%s %s" % (ref, surf), file=f)

    def addManualAnalysisInfo(self, base_ref, man_anal):
        if convert.OLBtoBETAtranslate(self.surface) != man_anal[0]:
            raise Exception("Error: word in manual_analyses.txt '%s %s %s %s' does not match up with surface of this one: '%s'" % (base_ref, man_anal[0], man_anal[1], man_anal[2], self.surface))
        self.parsing = man_anal[1]
        self.setStrongs(man_anal[2])

    def hasNoAnalysis(self):
        if self.parsing == "" or self.Strongs1 == -1:
            return True
        else:
            return False

    def hasAnalysis(self):
        return not self.hasNoAnalysis()


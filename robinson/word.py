from variant import *
from kind import *
import reader
import robinsontags
import convert

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

class Word:
    def __init__(self, monad, encoding):
        self.monad = monad
        self.encoding = encoding
        self.surface = ""
        self.accented_surface = ""
        self.parsing = ""
        self.strongslemma = ""
        self.ANLEXlemma = ""
        self.alt_parsing = ""
        self.Strongs1 = -1
        self.Strongs2 = -1
        self.Strongs3 = -1
        self.alt_Strongs1 = -1
        self.alt_Strongs2 = -1
        self.alt_Strongs3 = -1
        self.altlemma = ""
        self.tag_object = None

    def getStrongs(self):
        lemma = ""
        if self.Strongs1 != -1:
            lemma += str(self.Strongs1)
        if self.Strongs2 != -1:
            lemma += "&" + str(self.Strongs2)
        if self.Strongs3 != -1:
            lemma += "&" + str(self.Strongs3)
        return lemma

    def getAltStrongs(self):
        lemma = ""
        if self.alt_Strongs1 != -1:
            lemma += str(self.alt_Strongs1)
        if self.alt_Strongs2 != -1:
            lemma += "&" + str(self.alt_Strongs2)
        if self.alt_Strongs3 != -1:
            lemma += "&" + str(self.alt_Strongs3)
        return lemma

    def setStrongs(self, strongs):
        if "&" in strongs:
            mylist = strongs.split("&")
            self.Strongs1 = int(mylist[0])
            self.Strongs2 = int(mylist[1])
	    if len(mylist) == 3:
		self.Strongs3 = int(mylist[2])
        elif "/" in strongs:
            self.Strongs1 = strongs
        else:
            self.Strongs1 = int(strongs)

    def applyLemma(self, mapping, lemma_kind):
        strongs = self.getStrongs()
        if lemma_kind == kANLEX:
            self.ANLEXlemma = mapping.getLemmaFromStrongs(strongs)
        else:
            self.strongslemma = mapping.getLemmaFromStrongs(strongs)
            altStrongs = self.getAltStrongs()
            if altStrongs != "":
                self.altlemma = mapping.getLemmaFromStrongs(altStrongs)

    def getLemma(self):
        return self.strongslemma

    def convert2beta(self, mystr):
        if self.encoding == reader.read_OLB_encoding:
            return convert.OLBtoBETAtranslate(mystr)
        elif self.encoding == reader.read_UMAR_encoding:
            return convert.UMARtoBETAtranslate(mystr)
        else:
            raise Exception("Error: Unknwn self.encoding = %s" % self.encoding)

    def writeSFM(self, f, booknumber, chapter, verse, word_index, monad):
        print >>f, self.getSFMReference(f, booknumber, chapter, verse, word_index)
        if self.accented_surface != "":
            surfaceUTF8 = self.accented_surface
        else:
            surfaceUTF8 = self.beta2utf8(self.convert2beta(self.surface))
        print >>f, "\\text %s\r" % surfaceUTF8
        if len(self.parsing) > 0:
            print >>f, "\\pars %s\r" % self.parsing
        print >>f, "\\monad %d\r" % monad
        if self.ANLEXlemma == "":
            lemma = "NOLEMMA"
            #raise Exception("Error: lemma is empty.")
        else:
            lemma = self.ANLEXlemma
        if lemma != "":
            lemma_encoded = self.beta2utf8(lemma)
            print >>f, "\\lemma %s %s\r" % (self.getStrongs(), lemma_encoded)
        print >>f, "\\re\r"
        print >>f, "\r"

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
        result = ""
        for s in beta.split(" "):
            # Add '\n' at the end to convert final sigma to real final sigma.
            # The '\n' will be stripped out by the conversion
            utf16, remainder = convert.beta2unicodetrie.convert(s+"\n")

            # Convert Unicode string to UTF8
            utf8 = utf16.encode("utf-8")
            
            if remainder != "":
                #raise Exception("UTF8 = '" + utf8 +"'\nbeta = " + beta + "\n, and remainder was not empty, but was: '" + remainder + "'")
                print "UTF8 = '" + utf8 +"'\nbeta = " + beta + "\n, and remainder was not empty, but was: '" + remainder + "'"
            result += utf8 + " "
        return result[0:-1]

    def getSFMReference(self, f, booknumber, chapter, verse, word_index):
        return "\\rf %02d-%03d-%03d-%03d\r" % (int(booknumber), int(chapter), int(verse), int(word_index))

    def writeMQL(self, f, bUseOldStyle):
        if self.parsing != "":
            self.tag_object = robinsontags.RobinsonPierpontTag(self.parsing)
        else:
            self.tag_object = None
        print >>f, "CREATE OBJECT"
        print >>f, "FROM MONADS={%d}" % self.monad
        if bUseOldStyle:
            OT = "Word"
        else:
            OT = ""
        print >>f, "[%s" % OT

        if self.accented_surface != "":
            surfaceBETA = self.accented_surface
        else:
            surfaceBETA = self.convert2beta(self.surface)
        print >>f, "  surface:=\"%s\";" % convert.mangleMQLString(surfaceBETA)
        print >>f, "  surfaceutf8:=\"%s\";" % convert.mangleMQLString(self.beta2utf8(surfaceBETA))
        #print >>f, "  olb_surface:=\"%s\";" % self.surface
        if len(self.parsing) > 0:
            print >>f, "  parsing:=\"%s\";" % self.parsing
        if self.Strongs1 != -1:
            print >>f, "  strongs1:=%s;" % str(self.Strongs1)
        if self.Strongs2 != -1:
            print >>f, "  strongs2:=%s;" % str(self.Strongs2)
        if self.Strongs3 != -1:
            print >>f, "  strongs3:=%s;" % str(self.Strongs3)
        if len(self.alt_parsing) > 0:
            print >>f, "  alt_parsing:=\"%s\";" % self.alt_parsing
        if self.alt_Strongs1 != -1:
            print >>f, "  alt_strongs1:=%s;" % str(self.alt_Strongs1)
        if self.alt_Strongs2 != -1:
            print >>f, "  alt_strongs2:=%s;" % str(self.alt_Strongs2)
        if self.strongslemma == "":
            lemma = "NOLEMMA"
            #raise Exception("Error: lemma is empty for word with monad %d and surface %s" % (self.monad, self.surface))
        else:
            lemma = self.strongslemma
        if lemma != "":
            print >>f, "  lemmabeta:=\"%s\";" % lemma
            print >>f, "  lemmautf8:=\"%s\";" % self.beta2utf8(lemma)
        #if self.altlemma != "":
        #    print >>f, "  alt_lemmabeta:=\"%s\";" % self.altlemma
        #    print >>f, "  alt_lemmautf8:=\"%s\";" % self.beta2utf8(self.altlemma)
        if self.tag_object != None:
            self.tag_object.writeMQL(f)
        print >>f, "]"
        if bUseOldStyle:
            print >>f, "GO\n"
        else:
            print >>f, ""

    def writeSFMShort(self, f):
        print >>f, "\\text %s" % self.convert2beta(self.surface)
        print >>f, "\\monad %s" % str(self.monad)
        if len(self.parsing) > 0:
            print >>f, "\\pars %s" % self.parsing
        if self.Strongs1 != -1:
            print >>f, "\\str1 %d" % self.Strongs1
        if self.Strongs2 != -1:
            print >>f, "\\str2 %d" % self.Strongs2
        if self.Strongs3 != -1:
            print >>f, "\\str3 %d" % self.Strongs3
        if len(self.alt_parsing) > 0:
            print >>f, "\\altpars %s" % self.alt_parsing
        if self.alt_Strongs1 != -1:
            print >>f, "\\altstr1 %d" % self.alt_Strongs1
        if self.alt_Strongs2 != -1:
            print >>f, "\\altstr2 %d" % self.alt_Strongs2
        if self.alt_Strongs3 != -1:
            print >>f, "\\altstr3 %d" % self.alt_Strongs3
        print >>f, "\re\n"

    def parseStrongs(self, strongs):
        """This is necessary because "[tou 3588]" occurs in Romans, and
	qeou 2316> occurs in ByzParsed RE 21:2."""
        return strongs.replace(']', '').replace(">", "")

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
		    raise Exception("Error in words: word[index] is not kind_word:" + str(words[index:]))
		self.surface = words[index]
	
		# Advance index
		index += 1

		state = state_surface
	    elif state == state_surface:
		# Try next word
		kind = recognize(words[index])
		if kind == kind_number:
		    self.Strongs1 = int(self.parseStrongs(words[index]))
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
		    raise Exception("Error in Word.parse: 2: Unknown kind:" + str(kind) + " '" +str(words[index]) + "', words = " + str(words))
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

            

    def toStringMQL(self):
        result = ""
        result = result + "CREATE OBJECT\n"
        result = result + "FROM MONADS={%d}" % self.monad
        result = result + "["
        result = result + "  surface:=\"%s\";\n" % self.convert2beta(self.surface)
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

        result = result + "]"
        return result

    def toString(self):
        return "%-20s {%-15s %s}" % (self.surface, self.parsing, self.getStrongs())

    def write_MORPH_style(self, f, base_ref, index, bPrintLemma, encodingStyle):
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
        if self.accented_surface != "":
            surf = self.accented_surface
        else:
            surf = self.convert2beta(self.surface)

        if bPrintLemma:
            lemma = self.strongslemma
            ANLEXlemma = self.ANLEXlemma
            if lemma == "":
                print "Error: Strong's lemma for strong's %s does not exist. ref=%s surface=%s prs=%s" % (str(strongs), ref, surf, prs)
                lemma = "NOLEMMA"
                ANLEXlemma = "NOLEMMA"
            if ANLEXlemma == "":
                print "Error: ANLEX lemma for strong's %s does not exist. ref=%s surface=%s prs=%s" % (str(strongs), ref, surf, prs)
                ANLEXlemma = "NOLEMMA"

        if encodingStyle == kBETA:
            pass
        elif encodingStyle == kUnicode:
            lemma = self.beta2utf8(lemma)
            ANLEXlemma = self.beta2utf8(ANLEXlemma)
            surf = self.beta2utf8(surf)
        else:
            raise "Error: Unknown encodingStyle parameter = %s" % str(encodingStyle)

        if bPrintLemma:
            print >>f, "%s %s %s %s %s ! %s" % (ref, surf, prs, strongs, lemma, ANLEXlemma)
        else:
            print >>f, "%s %s %s %s" % (ref, surf, prs, strongs)

    def write_StrippedLinear(self, f, base_ref, index):
        ref = "%s" % base_ref
        print >>f, "%s %s" % (ref, convert.RemoveAccents(convert.MixedCaseBETAtoBETAtranslate(self.surface)))

    def write_WHLinear(self, f, base_ref, index):
        ref = "%s" % base_ref
        print >>f, "%s %s" % (ref, self.convert2beta(self.surface))

    def write_Linear(self, f, base_ref, index):
        ref = "%s" % base_ref
        if self.accented_surface != "":
            surf = self.accented_surface
        else:
            surf = self.convert2beta(self.surface)
        print >>f, "%s %s" % (ref, surf)

    def hasNoAnalysis(self):
        if self.parsing == "" or self.Strongs1 == -1:
            return True
        else:
            return False

    def hasAnalysis(self):
        return not self.hasNoAnalysis()


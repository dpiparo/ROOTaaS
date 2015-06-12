import re

from IPython.core.inputtransformer import InputTransformer
from IPython import get_ipython

import utils
import cppcompleter
import ROOT

def commentRemover( text ):
   def blotOutNonNewlines( strIn ) :  # Return a string containing only the newline chars contained in strIn
      return "" + ("\n" * strIn.count('\n'))

   def replacer( match ) :
      s = match.group(0)
      if s.startswith('/'):  # Matched string is //...EOL or /*...*/  ==> Blot out all non-newline chars
         return blotOutNonNewlines(s)
      else:                  # Matched string is '...' or "..."  ==> Keep unchanged
         return s

   pattern = re.compile(\
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE)

   return re.sub(pattern, replacer, text)

class CppTransformer(InputTransformer):

    def __init__(self):
        self.cell = ""
        self.mustSwitchToPython = False
        self.mustDeclare = False

    def push(self, line):
        # FIXME: must be in a single line
        fcnName="toPython()"
        if line == "%s;"%fcnName or line == fcnName:
            self.mustSwitchToPython = True
        elif line == ".dcl" and self.cell == "":
            self.mustDeclare = True
        else:
            if "" != self.cell:
               line+="\n"
            self.cell += line
        return None

    def reset(self):
        retval = 0
        if self.cell != "":
            if self.mustDeclare:
                retval = int(utils.declareCppCode(self.cell))
                self.mustDeclare = False
            else:
                cell = self.cell
                code = commentRemover(self.cell)
                #print cell
                #print "---"
                #print code
                retval = utils.processCppCode(code)
            self.cell = ""
        if self.mustSwitchToPython:
            unload_ipython_extension(get_ipython())
            self.mustSwitchToPython = False
            cppcompleter.unload_ipython_extension(get_ipython())
            print "Notebook is in Python mode"
        return str(retval)

_transformer = CppTransformer()

def unload_ipython_extension(ipython):
    ipython.input_splitter.logical_line_transforms.remove(_transformer)
    ipython.input_transformer_manager.logical_line_transforms.remove(_transformer)

def load_ipython_extension(ipython):
    ipython.input_splitter.logical_line_transforms.insert(0,_transformer)
    ipython.input_transformer_manager.logical_line_transforms.insert(0,_transformer)

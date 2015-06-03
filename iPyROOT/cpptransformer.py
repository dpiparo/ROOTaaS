import ROOT
import utils
from IPython.core.inputtransformer import InputTransformer
from IPython import get_ipython
import cppcompleter

def unload_ipython_extension(ipython):
    ipython.input_splitter.logical_line_transforms.pop()
    ipython.input_transformer_manager.logical_line_transforms.pop()

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
            self.cell += line
        return None

    def reset(self):
        retval = 0
        if self.cell != "":
            if self.mustDeclare:
                retval = int(utils.declareCppCode(self.cell))
                self.mustDeclare = False
            else:
                retval = utils.processCppCode(self.cell)
            self.cell = ""
        if self.mustSwitchToPython:
            unload_ipython_extension(get_ipython())
            self.mustSwitchToPython = False
            cppcompleter.unload_ipython_extension(get_ipython())
            print "Notebook is in Python mode"
        return str(retval)

_transformer = CppTransformer()

def load_ipython_extension(ipython):
    ipython.input_splitter.logical_line_transforms.append(_transformer)
    ipython.input_transformer_manager.logical_line_transforms.append(_transformer)

import ROOT
import utils
from IPython.core.inputtransformer import InputTransformer

class CppTransformer(InputTransformer):

    def __init__(self):
        self.cell = ""

    def push(self, line):
	self.cell += line
        return None
    
    def reset(self):
        retval = 0
        if self.cell != "":
            retval = utils.processCppCode(self.cell)
            self.cell = ""
        return str(retval)

         
def load_ipython_extension(ipython):
    t = CppTransformer()
    ipython.input_splitter.logical_line_transforms.append(t)
    ipython.input_transformer_manager.logical_line_transforms.append(t)


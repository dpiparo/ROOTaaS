import IPython.core.magic as ipym
import ROOT
import utils

@ipym.magics_class
class CppMagics(ipym.Magics):
    @ipym.cell_magic
    def cpp(self, line, cell=None):
        """Inject into root."""
        retval = 0
        if cell:
            retval = utils.processCppCode(cell)
        return retval

def load_ipython_extension(ipython):
    ipython.register_magics(CppMagics)


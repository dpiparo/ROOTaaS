import IPython.core.magic as ipym
import ROOT

@ipym.magics_class
class CppMagics(ipym.Magics):
    @ipym.cell_magic
    def cpp(self, line, cell=None):
        """Inject into root."""
        retval = 0
        if cell:
            retval = ROOT.gInterpreter.ProcessLine(cell)
        return 0

def load_ipython_extension(ipython):
    ipython.register_magics(CppMagics)


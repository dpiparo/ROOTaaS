import IPython.core.magic as ipym

@ipym.magics_class
class CppMagics(ipym.Magics):
    @ipym.cell_magic
    def cpp(self, line, cell=None):
        """Inject into root."""
        import ROOT
        if cell:
            return ROOT.gInterpreter.ProcessLine(cell)
        return 0

def load_ipython_extension(ipython):
    ipython.register_magics(CppMagics)


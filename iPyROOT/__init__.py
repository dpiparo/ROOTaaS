from IPython import get_ipython
from IPython.core.extensions import ExtensionManager
import ROOT
import utils

def iPythonize():
    utils.LoadLibrary("libRint.so")
    utils.setStyle()
    for capture in utils.captures: capture.register()
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.cppmagic")
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.dclmagic")

    ROOT.toCpp = utils.toCpp
    utils.welcomeMsg()


iPythonize()



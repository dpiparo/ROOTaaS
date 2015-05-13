import ROOT

clToiPythonize=[ROOT.TH1F]

def iPythonize(ROOTClasses):
    """
    Add an implementation of the __repr__ function which involves javascript
    and the json representation of the object.
    """
    for ROOTClass in ROOTClasses:
       ROOTClass.__repr__ = lambda obj: "Hello."


iPythonize(clToiPythonize)


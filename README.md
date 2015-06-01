# ROOTaaS
A tool to integrate the iPython notebooks, ROOT and jsROOT. This tool is an add-on to pyROOT and is still in the prototype phase.

## Example usage (from notebook)
```python
from ROOTaaS.iPyROOT import ROOT
h=ROOT.TH1F("h","jsHisto;X;Y",128,-4,4)
h.FillRandom("gaus")
h.Draw()

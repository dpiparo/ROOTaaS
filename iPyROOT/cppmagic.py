import os, sys, select, time
import IPython.core.magic as ipym
from IPython import get_ipython
from IPython.display import HTML
from IPython.display import display
import ROOT
import utils

_jsROOTSourceDir = "https://root.cern.ch/js/3.4/"
_jsCanvasWidth = 800
_jsCanvasHeight = 600

_jsCode = """
<div id="{jsDivId}"
     style="width: {jsCanvasWidth}px; height: {jsCanvasHeight}px">
</div>

<script>
require(['{jsROOTSourceDir}scripts/JSRootCore.min.js'],
        function() {{
            require(['{jsROOTSourceDir}scripts/d3.v3.min.js'],
                function() {{
                    require(['{jsROOTSourceDir}scripts/JSRootPainter.min.js'],
                        function() {{
define.amd = null;
JSROOT.source_dir = "{jsROOTSourceDir}";
var obj = JSROOT.parse('{jsonContent}');
JSROOT.draw("{jsDivId}", obj, "{jsDrawOptions}");
                        }}
                    );
                }}
            );
        }}
);
</script>
"""



@ipym.magics_class
class CppMagics(ipym.Magics):
    @ipym.cell_magic
    def cpp(self, line, cell=None):
        """Inject into root."""
        retval = 0
        if cell:
            for capture in utils.captures: capture.pre_execute()
            retval = ROOT.gInterpreter.ProcessLine(cell)
            for capture in utils.captures: capture.post_execute()
        return 0

def load_ipython_extension(ipython):
    ipython.register_magics(CppMagics)


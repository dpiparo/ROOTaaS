
import ROOT

# Jit a wrapper for the ttabcom
_TTabComHookCode = """
std::vector<std::string> _TTabComHook(const char* pattern){
  static auto ttc = new TTabCom;
  int pLoc = strlen(pattern);
  std::ostringstream oss;
  ttc->Hook((char* )pattern, &pLoc, oss);
  std::stringstream ss(oss.str());
  std::istream_iterator<std::string> vbegin(ss), vend;
  return std::vector<std::string> (vbegin, vend);
}
"""

class CppCompleter(object):

    def __init__(self):
        ROOT.gInterpreter.Declare(_TTabComHookCode)
        self.active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def complete(self, ip, event) :
        if self.active:
           return ROOT._TTabComHook(event.line)
        else:
           return []


_cppCompleter = CppCompleter()

def load_ipython_extension(ipython):
    _cppCompleter.activate()
    ipython.set_hook('complete_command', _cppCompleter.complete,re_key=r"(.+)")

def unload_ipython_extension(ipython):
    _cppCompleter.deactivate()

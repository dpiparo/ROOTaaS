
import re        

re_dot_match = re.compile(r"(.+)(\.)")

class CppCompleter(object):

    def __init__(self):
        self.active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def dot_completer(self, ip, event):
        # text ends in '.'
        if self.active:
            base = re_dot_match.split(event.line)[1]

            sugg = ['These', 'are', 'dummy', 'suggestions']
            return ["%s.%s" % (base, s) for s in sugg]
        else:
            return []

    def arrow_completer(self, ip, event):
        # text ends in '->'
        pass

    def doublecolon_completer(self, ip, event):
        # text ends in '::'
        pass

    def parenthesis_completer(self, ip, event):
        # text ends in '('
        pass

    def word_completer(self, ip, event):
        # text ends in a (possibly incomplete) word
        pass


c = CppCompleter()

def load_ipython_extension(ipython):
    c.activate()
    ipython.set_hook('complete_command', c.dot_completer, re_key=r"(.+)(\.)")
    # and others here

def unload_ipython_extension(ipython):
    c.deactivate()

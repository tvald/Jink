from creole import Parser
from creole.html_emitter import HtmlEmitter

from jinja2 import nodes
from jinja2.ext import Extension


class CreoleMarkupExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['markup'])
    
    def __init__(self, environment):
        super(CreoleMarkupExtension, self).__init__(environment)
    
    def parse(self, parser):
        # the first token is the token that started the tag, 'markup'
        # save the line number as a reference for the block
        lineno = parser.stream.next().lineno
        
        # now we parse the body of the block up to `endmarkup` and
        # drop the needle (which would always be `endmarkup` in that case)
        body = parser.parse_statements(['name:endmarkup'], drop_needle=True)
        
        # now return a `CallBlock` node that calls our _markup_support
        # helper method on this extension.
        return nodes.CallBlock(self.call_method('_markup_support', []),
                               [], [], body).set_lineno(lineno)
    
    def _markup_support(self, caller):
        """Helper callback."""
        document = Parser(caller()).parse()
        return HtmlEmitter(document).emit()

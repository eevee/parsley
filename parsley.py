from ometa.boot import BootOMetaGrammar
from ometa.runtime import ParseError, EOFError
from terml.parser import parseTerm as term
from terml.quasiterm import quasiterm

__version__ = '1.0pre2'

def makeGrammar(source, bindings, name='Grammar', unwrap=False):
    """
    Create a class from a Parsley grammar.

    @param source: A grammar, as a string.
    @param bindings: A mapping of variable names to objects.
    @param name: Name used for the generated class.

    @param unwrap: If True, return a parser class suitable for
    subclassing. If False, return a wrapper with the friendly API.
    """
    try:
        g = BootOMetaGrammar.makeGrammar(source, bindings, name=name)
    except ParseError, p:
        print p.formatError(source)
        raise
    return wrapGrammar(g)

def wrapGrammar(g):
    def makeParser(input):
        """
        Creates a parser for the given input, with methods for
        invoking each rule.

        @param input: The string you want to parse.
        """
        return _GrammarWrapper(g(input), input)
    return makeParser

class _GrammarWrapper(object):
    """
    A wrapper for Parsley grammar instances.

    To invoke a Parsley rule, invoke a method with that name. You can
    pass debug=True to rules for nicely formatted parse errors.

    This turns x(input).foo() calls into grammar.apply("foo") calls.
    """
    def __init__(self, grammar, input):
        self._grammar = grammar
        self._input = input
        #so pydoc doesn't get trapped in the __getattr__
        self.__name__ = _GrammarWrapper.__name__

    def __getattr__(self, name):
        """
        Return a function that will instantiate a grammar and invoke the named
        rule.
        @param: Rule name.
        """
        def doIt(*args, **kwargs):
            """
            Invoke a Parsley rule. Passes any positional args to the rule.

            Call with "debug=True" for nice formatting of errors.
            """
            debug = kwargs.get("debug", False)
            try:
                ret, err = self._grammar.apply(name, *args)
            except ParseError, e:
                err = e
            else:
                try:
                    extra, _ = self._grammar.input.head()
                except EOFError:
                    return ret

            if debug:
                print err.formatError(self._input)
                raise ParseError()
            else:
                raise err
        return doIt

__all__ = ['makeGrammar', 'term', 'quasiterm']

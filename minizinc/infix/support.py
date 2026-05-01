import pyparsing as pp

def exact(arg):
    return pp.one_of(arg)


def skip(arg):
    return pp.Suppress(exact(arg))


def kw(arg):
    return pp.one_of(arg, as_keyword=True)


def kwskip(arg):
    return pp.Suppress(kw(arg))


def opt(elem: pp.ParserElement):
    return pp.Opt(elem)


def iterate(production, separator, trailing=False):
    return pp.DelimitedList(production, delim=separator, allow_trailing_delim=trailing)


def delimit(left, production, right):
    return skip(left) + production + skip(right)

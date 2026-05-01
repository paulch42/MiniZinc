# MiniZinc Parser

This folder contains a parser for MiniZinc. The parser produces a Python object hierarchy that represents the MiniZinc model (abstract syntax tree), and the `__str__` functions recreate the model text from the obejcts. The generated text is a valid model and succeeds if fed back in to the parser or to MiniZinc. However, the text is not pretty printed.

The initial intent was to mimic the productions of the grammar in the [MiniZinc Manual](https://docs.minizinc.dev/en/stable/spec.html#full-grammar) and to create a coherent Python class hierarchy. The productions in the manual don't lend themselves well to that approach; they seem more oriented towards excluding as many invalid forms as possible through the grammar, but would lead to a more complex class hierarchy. The grammar presented here differs somewhat from the official grammar. It is simpler and more general, and as a consequence the parser accepts text that would be trapped as invalid by the MiniZinc parser.

|File|Content|
|----|-------|
|grammar.py|The MiniZinc grammar expressed in the [_pyparsing_](https://pypi.org/project/pyparsing/) framework.|
|support.py|General purpose functions used by the parser.|
|model.py. |A hierarchy of Python classes that represent a MiniZinc model.|
|actions.py|Parser actions that link the grammar to the class hierarchy (i.e. generate the abstract syntax tree).|
|mz.py     |Script to run the parser.|
|test.py   |A test suite for the parser using the [_pytest_](https://pypi.org/project/pytest/) framework.

The [models](models) folder contains some MiniZinc models used for testing. Some were obtained from the [MiniZinz Challenge](https://www.minizinc.org/challenge/) archive.

To run the parser:
```
python3 mz.py <file>
```
where `<file>` is the path to the MiniZinc file, but omits the `.mzn` file extension.

By default both inline and block comments are ignored. The command line argument `-inline` enables inline comments, and `-block` enables block comments. However, note the point in _Compliance_ below concerning comments.

The text version of the model generated from the abstract syntax tree is written to standard output.

## Compliance

The following are known issues with respect to compliance with the official MiniZinc grammar.

- A double quote `"` cannot appear in a string literal, even if escaped by `\`.
- Comments can be ignored or recorded in the parse tree. If ignored, comments can appear anywhere per the MiniZinc specification. If comments are recorded in the parse tree they can only appear between top-level model items.
- If inline comments are ignored (the default), the comment delimiter `%` cannot appear as the first non-white space character in a string literal.
- The last item in a model must be terminated with a `;`. MiniZinc allows `;` to be omitted from the last item.

## Performance

### Binary Operators

_pyparsing_ has a very convenient mechanism for handling precedence and associativity of binary  operators, via the [infix_notation](https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html#pyparsing.infix_notation) capability. The operators need only be configured and _pyparsing_ takes care of all precedence and associativity concerns during parsing. However, parsing performance suffers badly as the number of binary operators increases (even with _packrat_ enabled). It was necessary to handle binary operators via multiple levels of production, one per precedence level. The grammar is longer, but performance improved by an order of magnitude. Furthermore, when _pyparsing_ infix notation was used the default maximum recursion depth of Python, 1000, was easily exceeded and had to be increased to parse successfully.

The [infix](infix) folder contains an early version of the grammar that employs the _pyparsing_ infix notation.

### Grammar Complexity

The MiniZinc grammar is fairly complex, with deeply nested recursion. The parser takes around 2 seconds (elapsed) per 1000 lines of MiniZinc on a M2 MacBook Air with 24GB RAM. That includes parsing, creating the abstract syntax tree, and outputing the formatted text.

Performance is more of a problem parsing FlatZinc models due to their size. A 13000 line FlatZinc model (file size 1.1MB) takes around 25 seconds to process. To determine how much of this is due to the complexity of the grammar, a specific FlatZinc parser was created, which is far less complex and features a lower depth of recursion (see [flatzinc](../flatzinc)). The same 13000 line FlatZinc model takes under six seconds to process (a four-fold improvement).
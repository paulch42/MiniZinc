# FlatZinc Parser

This folder contains a parser for FlatZinc. It was created from the [MiniZinc parser](../minizinc) by removing those MiniZinc elements that are not part of FlatZinc, then some refactoring. More details are provided with the [MiniZinc parser](../minizinc). The contents are:

|File|Content|
|----|-------|
|grammar.py|The FlatZinc grammar expressed in the [_pyparsing_](https://pypi.org/project/pyparsing/) framework.|
|support.py|General purpoase functions used by the parser.|
|model.py. |A hierarchy of Python classes that represent a FlatZinc model.|
|actions.py|Parser actions that link the grammar to the class hierarchy (to generate the abstract syntax tree).|
|fz.py.    |Script to run the parser.|

The [models](models) folder contains some FlatZinc models used for testing. Some were generated from MiniZinc models that appeared in one of the [MiniZinc Challenges](https://www.minizinc.org/challenge/).

To run the parser:
```
python3 fz.py <file>
```
where `<file>` is the path to the FlatZinc file, but omits the `.fzn` file extension.

The text version of the model generated from the abstract syntax tree is written to standard output.
# source-code-analyzer
A CLI tool to analyze the complexity of functions and methods in your source code.

## How to use it

Provide the tool the path to a directory (that contains at least one `.py` file in one of its subdirectories) or a path to a `.py` file.

```bash
# analyse a whole directory
python src/code_complexity.py example

# analyse a single file
python src/code_complexity.py example/example1.py
```
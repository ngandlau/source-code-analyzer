# Source Code Analyzer

A CLI tool to analyze the complexity of functions and methods in your source code.

## Setup & Installation

The tool depends only on two external packages: 

```
astunparse==1.6.3
cognitive-complexity==1.3.0
```

## How to use it

Provide the tool the path to a directory (that contains at least one `.py` file in one of its subdirectories):

```bash
python src/code_complexity.py example

# === example/more_examples/example2.py === 

# function                                 | cognitive_complexity  | lines_of_code         | logical_lines_of_code | function_arguments   
# ---------------------------------------- | --------------------- | --------------------- | --------------------- | ---------------------
# add_numbers_complex                      | 1                     | 6                     | 6                     | 3                    
# add_numbers_simple                       | 0                     | 10                    | 7                     | 3                    



# === example/example1.py === 

# function                                 | cognitive_complexity  | lines_of_code         | logical_lines_of_code | function_arguments   
# ---------------------------------------- | --------------------- | --------------------- | --------------------- | ---------------------
# add_numbers_complex                      | 1                     | 6                     | 6                     | 3                    
# add_numbers_simple                       | 0                     | 10                    | 7                     | 3     
```

Or provide a path to a single python file:

```bash
python src/code_complexity.py example/example1.py

# === example/example1.py === 

# function                                 | cognitive_complexity  | lines_of_code         | logical_lines_of_code | function_arguments   
# ---------------------------------------- | --------------------- | --------------------- | --------------------- | ---------------------
# add_numbers_complex                      | 1                     | 6                     | 6                     | 3                    
# add_numbers_simple                       | 0                     | 10                    | 7                     | 3   
```

You can sort the table by the metric(s) that you like.

```bash
# sorts the table first by cognitive complexity, then by lines of code
python src/code_complexity.py src --sort cognitive_complexity lines_of_code
```

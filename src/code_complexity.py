import argparse
import ast
from typing import List, Tuple
from collections import namedtuple
import astunparse
import io
import tokenize

METRICS = ['lines_of_code', 'logical_lines_of_code', 'function_arguments']

FunctionName = str
MetricName = str
MetricValue = int
FunctionMetrics = namedtuple("FunctionMetrics", " ".join(METRICS))


def get_source_code(path: str) -> str:
    with open(path, 'r') as file:
        source_code = file.read()
    return source_code

def count_lines_of_code(node: ast.AST) -> int:
    """Counts a functions lines of code, including comments and docstrings."""
    start_line = node.lineno
    end_line = node.end_lineno
    num_lines = end_line - start_line + 1
    return num_lines

def count_docstring_lines(node: ast.AST) -> int:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring_node = node.body[0]
            return docstring_node.end_lineno - docstring_node.lineno + 1
    return 0

def count_comment_lines(node: ast.AST) -> int:
    function_source_code = astunparse.unparse(node)
    comment_lines = {token.start[0] for token in tokenize.generate_tokens(io.StringIO(function_source_code).readline) if token.type == tokenize.COMMENT}
    return len(comment_lines)

def count_logical_lines_of_code(node: ast.AST) -> int:
    """
    Counts a functions lines of code excluding comments and docstrings.

    #TODO: Currently counts an empty line as a logical line of code.
    """
    lines_of_code = count_lines_of_code(node)
    lines_of_docstring = count_docstring_lines(node)
    lines_of_comments = count_comment_lines(node)

    return lines_of_code - lines_of_docstring - lines_of_comments

def count_number_of_function_arguments(node: ast.AST) -> int:
    return len(node.args.args)

def calculate_complexity_of_functions(path: str) -> List[Tuple[FunctionName, FunctionMetrics]]:
    source_code = get_source_code(path)
    tree = ast.parse(source_code)

    data = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            function_metrics = FunctionMetrics(
                lines_of_code=count_lines_of_code(node),
                logical_lines_of_code=count_logical_lines_of_code(node),
                function_arguments=count_number_of_function_arguments(node)
            )
            data.append((function_name, function_metrics))
    
    return data

def print_pretty_table(data: List[Tuple[FunctionName, FunctionMetrics]]):
    columns = ['function', *FunctionMetrics._fields]

    # table header
    print(" | ".join(["{:<20}".format(column) for column in columns]))

    # row of dashes
    print(" | ".join(["{:<20}".format("-"*20) for column in columns]))

    # rows
    for function_name, function_metrics in data:
        values = (function_name, *function_metrics)
        print(" | ".join(["{:<20}".format(column) for column in values]))


def main(path):
    function_complexities = calculate_complexity_of_functions(path=path)
    print_pretty_table(function_complexities)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file at a given path.')
    parser.add_argument('path', type=str, help='the path to the file')

    args = parser.parse_args()

    main(args.path)
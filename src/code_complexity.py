import argparse
import ast
from typing import Dict, List, Tuple
from collections import namedtuple

METRICS = ['lines_of_code']

FunctionName = str
MetricName = str
MetricValue = int
FunctionMetrics = namedtuple("FunctionMetrics", *METRICS)


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

def calculate_complexity_of_functions(path: str) -> List[Tuple[FunctionName, FunctionMetrics]]:
    source_code = get_source_code(path)
    tree = ast.parse(source_code)

    data = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            function_metrics = FunctionMetrics(
                lines_of_code=count_lines_of_code(node),
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
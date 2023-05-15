import argparse
import ast
from typing import List, Tuple
from collections import namedtuple
import astunparse
import io
import tokenize
from cognitive_complexity.api import get_cognitive_complexity

METRICS = [
    "lines_of_code",
    "logical_lines_of_code",
    "function_arguments",
    "cognitive_complexity",
]

FunctionName = str
MetricName = str
MetricValue = int
FunctionMetrics = namedtuple("FunctionMetrics", " ".join(METRICS))


def get_source_code(path: str) -> str:
    with open(path, "r") as file:
        source_code = file.read()
    return source_code


def count_lines_of_code(node: ast.AST) -> int:
    """Counts a functions lines of code, including comments and docstrings."""
    start_line = node.lineno
    end_line = node.end_lineno
    num_lines = end_line - start_line + 1
    return num_lines


def count_docstring_lines(node: ast.AST) -> int:
    if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
    ):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        ):
            docstring_node = node.body[0]
            return docstring_node.end_lineno - docstring_node.lineno + 1
    return 0


def count_comment_lines(node: ast.AST) -> int:
    function_source_code = astunparse.unparse(node)
    comment_lines = {
        token.start[0]
        for token in tokenize.generate_tokens(
            io.StringIO(function_source_code).readline
        )
        if token.type == tokenize.COMMENT
    }
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


def calculate_function_metrics(
    path: str,
) -> List[Tuple[FunctionName, FunctionMetrics]]:
    source_code = get_source_code(path)
    tree = ast.parse(source_code)

    function_data = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            function_metrics = FunctionMetrics(
                lines_of_code=count_lines_of_code(node),
                logical_lines_of_code=count_logical_lines_of_code(node),
                function_arguments=count_number_of_function_arguments(node),
                cognitive_complexity=get_cognitive_complexity(node),
            )
            function_data.append((function_name, function_metrics))

    return function_data


def sort_function_metrics(
    function_metrics: List[Tuple[FunctionName, FunctionMetrics]],
    sort_by_metric="cognitive_complexity",
) -> List[Tuple[FunctionName, FunctionMetrics]]:
    sorted_function_metrics = sorted(
        function_metrics,
        key=lambda data: getattr(data[1], sort_by_metric),
        reverse=True
    )
    return sorted_function_metrics


def print_pretty_table(data: List[Tuple[FunctionName, FunctionMetrics]]):
    columns = ["function", *FunctionMetrics._fields]

    # table header
    print(" | ".join(["{:<20}".format(column) for column in columns]))

    # row of dashes
    print(" | ".join(["{:<20}".format("-" * 20) for column in columns]))

    # rows
    for function_name, function_metrics in data:
        values = (function_name, *function_metrics)
        print(" | ".join(["{:<20}".format(column) for column in values]))


def main(path: str, sort_by_metric: str):
    function_metrics = calculate_function_metrics(path=path)
    sorted_function_metrics = sort_function_metrics(function_metrics, sort_by_metric=sort_by_metric)
    print_pretty_table(sorted_function_metrics)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file at a given path.")
    parser.add_argument("path", type=str, help="the path to the file")
    parser.add_argument("sort_by_metric", type=str, default="cognitive_complexity", help="sort functions according to a metric", choices=METRICS)

    args = parser.parse_args()

    main(args.path, args.sort_by_metric)

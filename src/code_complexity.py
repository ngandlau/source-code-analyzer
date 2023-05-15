import argparse
import ast
from typing import List, Tuple
from collections import namedtuple
import astunparse
import io
import tokenize
from cognitive_complexity.api import get_cognitive_complexity
from pathlib import Path

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


def get_source_code(path: Path) -> str:
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
    path_to_file: Path,
) -> List[Tuple[FunctionName, FunctionMetrics]]:
    source_code = get_source_code(path_to_file)
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


def print_pretty_table(function_data: List[Tuple[FunctionName, FunctionMetrics]]):
    # print table header
    print(" | ".join(["{:<40}".format("function")] + ["{:<21}".format(metric_name) for metric_name in FunctionMetrics._fields]))
    print(" | ".join(["{:<40}".format("-" * 40)  ] + ["{:<21}".format("-" * 21) for metric_name in FunctionMetrics._fields]))

    # print one row per function
    for function_name, function_metrics in function_data:
        if len(function_name) >= 36:
            function_name = function_name[:36] + "..."
        print(" | ".join(["{:<40}".format(function_name)] + ["{:<21}".format(metric_value) for metric_value in function_metrics]))

def analyze_file(path: Path, sort_by_metric: str):
        function_metrics = calculate_function_metrics(path)
        sorted_function_metrics = sort_function_metrics(
            function_metrics=function_metrics,
            sort_by_metric=sort_by_metric
        )
        print(f"=== {path.as_posix()} === \n")
        print_pretty_table(sorted_function_metrics)
        print(f"\n\n")

def analyze_files(path: Path, sort_by_metric: str):
    if path.is_file():
        if path.suffix == '.py':
            analyze_file(path, sort_by_metric)
    elif path.is_dir():
        for file in path.iterdir():
            analyze_files(file, sort_by_metric)
    else:
        raise FileNotFoundError(f"is {path} empty? it contains neither files nor directories.")


def main(path: str, sort_by_metric: str):
    analyze_files(Path(path), sort_by_metric)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file at a given path.")
    parser.add_argument("path", type=str, help="the path to the file")
    parser.add_argument("--sort", type=str, default="cognitive_complexity", help="the metric to sort functiony by", choices=METRICS)

    args = parser.parse_args()

    main(args.path, args.sort)

import ast
import operator as op
import re
from datetime import datetime, timezone

_ops = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        return float(_ops[type(node.op)](_eval_node(node.left), _eval_node(node.right)))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return float(_ops[ast.USub](_eval_node(node.operand)))
    raise ValueError("nope")


def calculate(expr):
    expr = expr.strip().replace(" ", "")
    tree = ast.parse(expr, mode="eval")
    return f"{expr} = {_eval_node(tree.body)}"


def run_tool_if_needed(msg):
    low = msg.lower()
    if "what time" in low or "current time" in low:
        t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"Current time: {t}"

    m = re.search(r"(?:calculate|compute|what is)\s+([\d\.\+\-\*\/\(\)\s]+)", msg, re.I)
    if m:
        try:
            return calculate(m.group(1))
        except Exception:
            return "couldn't parse that math"

    if re.fullmatch(r"[\d\.\+\-\*\/\(\)\s]+", msg.strip()):
        try:
            return calculate(msg.strip())
        except Exception:
            pass
    return None

import ast
import operator as op
import re
from datetime import datetime, timezone

_ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}


def _eval_expr(node):
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        return _ops[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_expr(node.operand)
    raise ValueError("bad expr")


def run_tools(msg):
    low = msg.lower()
    if "time" in low and ("what" in low or "current" in low):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    m = re.search(r"(?:calculate|compute|what is)\s+([\d\.\+\-\*\/\(\)\s]+)", msg, re.I)
    if m:
        try:
            e = m.group(1).strip().replace(" ", "")
            v = _eval_expr(ast.parse(e, mode="eval").body)
            return f"{m.group(1).strip()} = {v}"
        except Exception:
            return None

    if re.fullmatch(r"[\d\.\+\-\*\/\(\)\s]+", msg.strip()):
        try:
            e = msg.strip().replace(" ", "")
            v = _eval_expr(ast.parse(e, mode="eval").body)
            return f"{msg.strip()} = {v}"
        except Exception:
            pass
    return None

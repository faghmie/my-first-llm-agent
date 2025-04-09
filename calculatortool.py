import math 
from tool import Tool

class CalculatorTool(Tool):
    def name(self):
        return "Calculator Tool"

    def description(self):
        return """Evaluates simple mathematical expressions. 
            Supports operations like addition, subtraction, multiplication, and division. 
            arguments should be passed as a simple string with the correct mathematical symbols.
            Ensure that all unnecessary spaces are removed.
            When evaluating an expression, the following english words should converted to their mathematical symbols:
            divide or divide by = /
            plus or add = +
            mius or subtract = -
            multiply or times = *
            
            """

    def use(self, *args, **kwargs):
        expression = args[0]
        try:
            # Evaluate the expression safely
            result = self.safe_eval(expression)
            return f"The result of '{expression}' is {result}."
        except Exception as e:
            return f"Sorry, I couldn't evaluate the expression '{expression}'. Error: {str(e)}"

    def safe_eval(self, expression):
        # Allowed names
        allowed_names = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'pow': pow,
            'sqrt': math.sqrt,
            'log': math.log,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi,
            'e': math.e
        }

        allowed_chars = "0123456789+-*/()., "

        if any(char not in allowed_chars for char in expression):
            raise ValueError("Invalid characters in expression.")

        code = compile(expression, "<string>", "eval")

        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"Use of '{name}' is not allowed.")

        return eval(code, {"__builtins__": None}, allowed_names)
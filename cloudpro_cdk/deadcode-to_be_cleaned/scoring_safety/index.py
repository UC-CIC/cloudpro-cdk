import json
import ast
import operator

class ScoringSafety:
    MAX_FORMULA_LENGTH = 255

    def __init__(self,formula:str):
        self.formula = formula

        # mapping allowed AST operations to check handlers.
        self.EVALUATORS = {
            ast.Compare: self.eval_compare,
            ast.IfExp: self.eval_ifexp,
            ast.BinOp: self.eval_binop,
            ast.BoolOp: self.eval_boolop,
            ast.Subscript: self.eval_subscript,
            ast.Call: self.eval_call,
            ast.Constant: self.eval_constant,
            ast.Name: self.eval_name
        }
        return self.verify_formula()

    def verify_formula( self ):
        if len(self.formula) > self.MAX_FORMULA_LENGTH:
            raise Exception("The formula is too long")
    
        try:
            st = ast.parse(self.formula, mode='eval')
        except Exception as e:
            raise Exception(f"Invalid expression: {e}")
    
        try:
            return self.formula_safety( st )
        except Exception as e:
            raise Exception(f"Formula is not safe: {e}")
           
    def formula_safety( self, st ):
        self._validate(st.body)

    def _validate(self,node):
        try:
            try:
                # make sure the node has been approved
                evaluate_ast = self.EVALUATORS[type(node)]
            except:
                raise Exception(f"Unsupported node {node!r}")
            # execute handler
            evaluate_ast(node)
        except Exception as e:
            raise Exception(f"{e}")

    # allow constants
    def eval_constant(self,node):
        pass       

    # allow binary operators
    def eval_binop(self,node):
        # allow list for accepted binary operators
        OPERATIONS = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

        try:
            apply = OPERATIONS[type(node.op)]
        except:
            raise Exception(f"Unsupported operation {node.op!r}")
        
        # binary operator will have a left and right node we must explore
        self._validate(node.left)
        self._validate(node.right)

    def eval_boolop(self,node):
        # allow list for accepted bool operators
        BOOLOPS = {
            ast.And: operator.and_,
            ast.Or: operator.or_
        }
        
        try:
            apply = BOOLOPS[type(node.op)]
        except:
            raise Exception(f"Unsupported operation {node.op!r}")
        
        # we must explore each value of the bool list and validate
        [self._validate(value) for value in node.values]
        

    # allow comparison operator
    def eval_compare(self,node):
        self._validate(node.left)
        [self._validate(c) for c in node.comparators ]

    # allow if else in expression
    def eval_ifexp(self,node):
        self._validate(node.body)
        self._validate(node.test)
        self._validate(node.orelse)

    # allow access to dictionaries
    def eval_subscript(self,node):
        self._validate(node.value)

    # allow certain variable names
    def eval_name(self,node):
        if node.id not in ["cpro_loader"]:
            raise Exception(f"{node.id!r} not found")

    # allow certain function calls
    def eval_call(self,node):
        if isinstance(node.func, ast.Name):
            # allow use of len
            if node.func.id not in ("len",):
                raise Exception(f"{node.func.id!r} not found.")
            else:
                [self._validate(arg) for arg in node.args]
        # Allow use of startswith, endswith
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr not in ("startswith", "endswith"):
                raise Exception(f"{node.func.attr!r} not found.")
        else:
            raise Exception(f"Unsupported node {node!r}")

def handler(event,context):
    sanitized_formula=""
    error_msg=""
    status_code=500
    try:
        sanitized=ScoringSafety(event['body'])
        sanitized_formula=sanitized.formula
        status_code=200
    except Exception as e:
        error_msg=str(e)
        status_code=500

    payload = {
        "sanitized_formula":sanitized_formula,
        "error_msg":error_msg
    }
    return {
        "statusCode":status_code,
        "body":json.dumps(payload)
    }
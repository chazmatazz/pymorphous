from ast import *

class PymorphousVisitor(NodeTransformer):

    def visit_Call(self, node):
        stmts = []
        if isinstance(node.func, Name):
            if node.func.id == 'let2':
                for tup in node.args[0].elts:
                    stmts += [fix_missing_locations(Assign([Name(tup.elts[0].id, Store())], tup.elts[1]))]
                return stmts + [self.generic_visit(node.args[1])] 
        return [self.generic_visit(node)]

def transform(ast):
    return PymorphousVisitor().visit(ast)

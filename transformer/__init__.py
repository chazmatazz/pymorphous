from ast import *

class Scopify(NodeTransformer):
    """ 
    Generate scopes
    """
    pass

class Uniquify(NodeTransformer):
    """
    Uniquify variables
    """
    pass

class CollectNbr(NodeTransformer):
    def __init__(self):
        self.nbr_vars = set()
    
    def visit_Module(self, node):
        print dump(node)
        return self.generic_visit(node)
    
    def visit_Call(self, node):
        #print dump(node)
        if isinstance(node.func, Attribute) and node.func.attr == 'nbr':
            self.nbr_vars |= set(node.args)
        return self.generic_visit(node)
    
class Neighborify(NodeTransformer):
    def __init__(self, nbr_vars):
        self.nbr_vars = nbr_vars
        
    def visit_Func(self, node):
        print dump(node)
        return self.generic_visit(node)

def transform(ast):
    Scopify().visit(ast)
    new_ast = Uniquify().visit(ast)
    collect_nbr = CollectNbr()
    collect_nbr.visit(new_ast)
    return Neighborify(collect_nbr.nbr_vars).visit(new_ast) 

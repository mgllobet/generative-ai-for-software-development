import ast
import json
from termcolor import colored
import os


# Objects that are present in the graded cells. If it not resent here, then if found in the graded cell, the test will automatically fail.
IMPORTANT_OBJECTS = {'imports': (ast.Import, ast.ImportFrom),
                     'functions': ast.FunctionDef,
                     #'assigns': ast.Assign,
                     'classes': ast.ClassDef}

# Dictionary with the graded cells informations, to be compared with the graded cells in the notebook.
CONDITIONS_DICT=[{'cell_number': 0,
  'has_imports': True,
  'has_functions': False,
  'has_classes': True,
  'imports': [{'module': 'random', 'submodules': [], 'start': 0, 'end': 1},
   {'module': 'heapq', 'submodules': [], 'start': 1, 'end': 2},
   {'module': 'itertools', 'submodules': [], 'start': 2, 'end': 3}],
  'classes': [{'name': 'Graph',
    'methods': [{'function': '__init__',
      'args': {'arg_names': ['self', 'directed'],
       'has_non_constant_args': False},
      'has_return': False,
      'start': 5,
      'end': 18},
     {'function': 'add_vertex',
      'args': {'arg_names': ['self', 'vertex'],
       'has_non_constant_args': False},
      'has_return': False,
      'start': 19,
      'end': 32},
     {'function': 'add_edge',
      'args': {'arg_names': ['self', 'src', 'dest', 'weight'],
       'has_non_constant_args': False},
      'has_return': False,
      'start': 33,
      'end': 50},
     {'function': 'remove_edge',
      'args': {'arg_names': ['self', 'src', 'dest'],
       'has_non_constant_args': False},
      'has_return': False,
      'start': 51,
      'end': 64},
     {'function': 'remove_vertex',
      'args': {'arg_names': ['self', 'vertex'],
       'has_non_constant_args': False},
      'has_return': False,
      'start': 65,
      'end': 79},
     {'function': 'get_adjacent_vertices',
      'args': {'arg_names': ['self', 'vertex'],
       'has_non_constant_args': False},
      'has_return': True,
      'start': 80,
      'end': 91},
     {'function': 'tour_length',
      'args': {'arg_names': ['self', 'tour'], 'has_non_constant_args': False},
      'has_return': True,
      'start': 92,
      'end': 111},
     {'function': '_get_edge_weight',
      'args': {'arg_names': ['self', 'src', 'dest'],
       'has_non_constant_args': False},
      'has_return': True,
      'start': 112,
      'end': 124},
     {'function': '__str__',
      'args': {'arg_names': ['self'], 'has_non_constant_args': False},
      'has_return': True,
      'start': 125,
      'end': 133}],
    'start': 4,
    'end': 133}],
  'functions': None},
 {'cell_number': 1,
  'has_imports': False,
  'has_functions': False,
  'has_classes': True,
  'imports': None,
  'classes': [{'name': 'GraphShortestPath',
    'methods': [{'function': 'shortest_path',
      'args': {'arg_names': ['self', 'start', 'end'],
       'has_non_constant_args': False},
      'has_return': True,
      'start': 4,
      'end': 37}],
    'start': 2,
    'end': 37}],
  'functions': None},
 {'cell_number': 2,
  'has_imports': False,
  'has_functions': False,
  'has_classes': True,
  'imports': None,
  'classes': [{'name': 'GraphTSPSmallGraph',
    'methods': [{'function': 'tsp_small_graph',
      'args': {'arg_names': ['self', 'start_vertex'],
       'has_non_constant_args': False},
      'has_return': True,
      'start': 3,
      'end': 40}],
    'start': 2,
    'end': 40}],
  'functions': None},
 {'cell_number': 3,
  'has_imports': False,
  'has_functions': False,
  'has_classes': True,
  'imports': None,
  'classes': [{'name': 'GraphTSPLargeGraph',
    'methods': [{'function': 'tsp_large_graph',
      'args': {'arg_names': ['self', 'start'], 'has_non_constant_args': False},
      'has_return': True,
      'start': 3,
      'end': 60}],
    'start': 2,
    'end': 60}],
  'functions': None},
 {'cell_number': 4,
  'has_imports': False,
  'has_functions': False,
  'has_classes': True,
  'imports': None,
  'classes': [{'name': 'GraphTSPMediumGraph',
    'methods': [{'function': 'tsp_medium_graph',
      'args': {'arg_names': ['self', 'start'], 'has_non_constant_args': False},
      'has_return': True,
      'start': 3,
      'end': 39}],
    'start': 2,
    'end': 39}],
  'functions': None}]

# The amount of graded cells that are not in fact graded (imports cells and other auxiliary cells that are graded for grading purposes).
GRADED_SHIFT = 1


def metric(s):
    if 'solution' in s:
        return 0
    elif 'Solution' in s:
        return 1
    else:
        return 2

possible_files = [x for x in os.listdir() if 'ipynb' in x]
possible_files.sort(key = metric)

path = possible_files[0]

class GradedTree():
    def __init__(self, tree):
        self.tree = tree
        self.objects = tree.body
        for name, object in IMPORTANT_OBJECTS.items():
            if len([x for x in tree.body if isinstance(x, object)]) != 0:
                setattr(self, f"has_{name}", True)
            else:
                setattr(self, f"has_{name}", False)
        if len([x for x in tree.body if not isinstance(x, tuple(IMPORTANT_OBJECTS.values()))]) != 0:
            self.has_other_values = True
        else:
            self.has_other_values = False
            
    def get_imports(self):
        if not self.has_imports:
            return None
        all_imports = [x for x in self.objects if isinstance(x, IMPORTANT_OBJECTS['imports'])]
        imports = []
        for val in all_imports:
            import_dict = {'module': '', 'submodules':[], 'start':-1, 'end':-1}
            import_dict['start'] = val.lineno - 1
            import_dict['end'] = val.end_lineno
            no_sub_import = False
            try:
                import_dict['module'] = val.module
            except:
                no_sub_import = True
            if no_sub_import:
                for x in val.names:
                    import_dict['module'] = x.name
            else:
                for x in val.names:
                    import_dict['submodules'].append(x.name)
            imports.append(import_dict)
        return imports
    
    def get_functions(self):
        if not self.has_functions:
            return None
        all_functions = [x for x in self.objects if isinstance(x, IMPORTANT_OBJECTS['functions'])]
        functions = []
        for function in all_functions:
            function_dict = {'function':'', 'args': {"arg_names":[], 'has_non_constant_args': False}, 'has_return':False, 'start':-1, 'end':-1}
            function_dict['function'] = function.name
            function_dict['start'] = function.lineno - 1
            function_dict['end'] = function.end_lineno
            for arg in function.args.args:
                arg_name = arg.arg
                function_dict['args']['arg_names'].append(arg_name)
            non_constant_args = [x for x in function.args.defaults if not isinstance(x, ast.Constant)]
            if len(non_constant_args) != 0:
                function_dict['args']['has_non_constant_args'] = True
            for object in function.body:
                if isinstance(object, ast.Return):
                    function_dict['has_return'] = True
                    break
            functions.append(function_dict)
                
        return functions
    
    def _get_functions(self, function):
        function_dict = {'function':'', 'args': {"arg_names":[], 'has_non_constant_args': False}, 'has_return':False, 'start':-1, 'end':-1}
        function_dict['function'] = function.name
        function_dict['start'] = function.lineno - 1
        function_dict['end'] = function.end_lineno
        for arg in function.args.args:
            arg_name = arg.arg
            function_dict['args']['arg_names'].append(arg_name)
        non_constant_args = [x for x in function.args.defaults if not isinstance(x, ast.Constant)]
        if len(non_constant_args) != 0:
            function_dict['args']['has_non_constant_args'] = True
        for object in function.body:
            if isinstance(object, ast.Return):
                function_dict['has_return'] = True
                break         
        return function_dict
    
    def get_assigns(self):
        if not self.has_assigns:
            return None
        all_assigns = [x for x in self.objects if isinstance(x,IMPORTANT_OBJECTS['assigns'])]
        assigns = []
        for assign in all_assigns:
            assign_dict = {'start': -1, 'end': -1}
            assign_dict['start'] = assign.lineno - 1
            assign_dict['end'] = assign.end_lineno
            assigns.append(assign_dict)
        return assigns
    
    
    def get_classes(self):
        if not self.has_classes:
            return None
        all_classes = [x for x in self.objects if isinstance(x,IMPORTANT_OBJECTS['classes'])]
        classes = []
        for class_ in all_classes:
            class_dict = {'name':'', 'methods':[], 'start':-1, 'end':-1}
            class_dict['start'] = class_.lineno - 1
            class_dict['end'] = class_.end_lineno
            class_dict['name'] = class_.name
            methods = [self._get_functions(x) for x in class_.body if isinstance(x, IMPORTANT_OBJECTS['functions'])]
            class_dict['methods'] = methods
            classes.append(class_dict)
        return classes
    
    def get_other_values(self):
        if not self.has_other_values:
            return None
        else:
            all_other_values = [x for x in self.objects if not isinstance(x, tuple(IMPORTANT_OBJECTS.values()))]
            other_values = []
            for other_value in all_other_values:
                other_value_dict = {'start':-1, 'end':-1}
                other_value_dict['start'] = other_value.lineno - 1
                other_value_dict['end'] = other_value.end_lineno
                other_values.append(other_value_dict)
        return other_values
    
    def gen_conditions_dict(self, cell_number = 0):
        conditions_dict = {'cell_number': cell_number}
        conditions_dict['has_imports'] = self.has_imports
        conditions_dict['has_functions'] = self.has_functions
        conditions_dict['has_classes'] = self.has_classes
        conditions_dict['imports'] = self.get_imports()
        conditions_dict['classes'] = self.get_classes()
        conditions_dict['functions'] = self.get_functions()
        return conditions_dict




        
def load_nb(path):
    with open(path, 'r') as notebook_file:
        notebook_data = json.load(notebook_file)
        return notebook_data
    
def get_graded_cells(nb, conditions_dict = None):
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    if len(code_cells) == 0:
        return (False, colored('No code cells found in your notebook. Please refresh your workspace','red'))
    text_case_fails = colored("You deleted one or more graded cell. Please refresh your workspace and copy your solution in the cells that the graded functions are initially. Autograder will fail as it won't find these solutions.\nTo refresh work workspace, follow the instructions in the coursera item called '(Optional) Downloading your Notebook and Refreshing your Workspace.'", 'red')
    tagged_cells = [c for c in code_cells if 'tags' in c['metadata'].keys()]
    if len(tagged_cells) == 0:
        return False, text_case_fails
    graded_cells = [c for c in tagged_cells if ('graded' in c['metadata']['tags'])]
    if conditions_dict is not None:
        if len(graded_cells) < len(conditions_dict):
            for graded_cell in graded_cells:
                tree, code = parse_graded_cell(graded_cell)
                graded_tree = GradedTree(tree)
                has_initial_import_cell = False
                if (graded_tree.has_imports == True) and (graded_tree.has_other_values == False) and (graded_tree.has_classes == False) and (graded_tree.has_functions == False):
                    has_initial_import_cell = True
            if not has_initial_import_cell:
                return False, colored("You deleted the initial import cell and moved it to another cell. This will break the autograder. Please refresh your workspace and paste your solution there.\nTo refresh work workspace, follow the instructions in the coursera item called '(Optional) Downloading your Notebook and Refreshing your Workspace.' ",'red')
            return False, text_case_fails
    return (True, graded_cells)

def parse_graded_cell(graded_cell: dict):
    if not isinstance(graded_cell, dict):
        raise Exception('graded_cell must be a dictionary with the graded cell information')
    source = graded_cell['source']
    code = "".join(source)
    tree = ast.parse(code)
    return tree, source

def cell_checker(tree, code, cell_number, conditions_dict):
    graded_tree = GradedTree(tree)
    has_attrs = [attr for attr in dir(graded_tree) if 'has_' in attr]
    for attr in has_attrs:
        if attr not in conditions_dict.keys():
            conditions_dict[attr] = False
    imports = graded_tree.get_imports()
    functions = graded_tree.get_functions()
    classes = graded_tree.get_classes()
    other_values = graded_tree.get_other_values()
    if (functions is None) and conditions_dict['has_functions']:
        return False, colored(f"There is no function detected in graded cell number {cell_number}. Autograder will likely fail. Make sure you haven't moved the functions to another cell.", 'red')
    if (imports is None) and conditions_dict['has_imports']:
        return False, colored(f"There is no import detected in graded cell number {cell_number}. Autograder will likely fail. Make sure you haven't moved the imports to another cell.", 'red')
    if (classes is None) and conditions_dict['has_classes']:
        return False, colored(f"There is no class object detected in graded cell number {cell_number}. Autograder will likely fail. Make sure you haven't moved the classes to another cell." , 'red')

    if (imports is not None) and (not conditions_dict['has_imports']):
        msg = colored(f"There is one or more import detected in graded cell number {cell_number} where it should have any. Autograder will likely fail. Do not add new imports in a cell apart from the ones in the beginning, or the ones that are already in the graded cell. Imports that should not exist in this cell:\n", 'red')
        for import_ in imports:
            msg += "".join(code[import_['start']:import_['end']])
        return False, msg

    if (other_values is not None):
        msg = colored(f"There is more content in graded cell number {cell_number} than it should have. Autograder will likely fail. Please remove them before submitting. Content that must be removed or moved to the correct place:\n",'red')
        for other_value in other_values:
            msg += "".join(code[other_value['start']:other_value['end']]) + '\n'
        return False, msg
    if (functions is not None) and (not conditions_dict['has_functions']):
        msg = colored(f"Function(s) detected in graded cell number {cell_number} where it shouldn't have a function. The function(s) to be removed or moved to the correct place:\n",'red')
        for function in functions:
            msg += "".join(code[function['start']:function['end']]) + '\n'
        return False, msg
    if (classes is not None) and (not conditions_dict['has_classes']):
        msg = colored(f"Class(es) detected in a graded cell number {cell_number} where it shouldn't have a class. The class(es) to be removed or moved to the correct place:\n", 'red')
        for class_ in classes:
            msg += "".join(code[class_['start']:class_['end']])
        return False, msg
    
    if (imports is not None) and conditions_dict['has_imports']:
        condition_modules = list(set([x['module'] for x in conditions_dict['imports']]))
        got_modules = list(set([x['module'] for  x in imports]))
        condition_modules.sort()
        got_modules.sort()
        if (condition_modules) != (got_modules):
            msg = colored(f"Incorrect imports. Autograder may fail. Make sure you haven't added or removed imports from graded cell number {cell_number}.\n",'red')
            msg += f"Expected imports: {condition_modules}\n"
            msg += f"Imports got: {got_modules}"
            return False, msg
        for module in (condition_modules):
            condition_submodules = list(set([x['submodules'] for x in conditions_dict['imports'] if x['module'] == module][0]))
            got_submodules = list(set([x['submodules'] for x in imports if x['module'] == module][0]))
            condition_submodules.sort()
            got_submodules.sort()
            if condition_submodules != got_submodules:
                msg = colored(f"Incorrect submodules/functions imported from module {module} in cell number {cell_number}. Make sure you haven't added or removed any function/submodule in module {module}, otherwise autograder is likely to fail.\n", 'red')
                msg += f"Expected: module: {module}, submodules: {condition_submodules}\n"
                msg += f"Got: module {module}, submodules {got_submodules}"
                return False, msg
        
    if (functions is not None) and conditions_dict['has_functions']:
        condition_functions = list(set([x['function'] for x in conditions_dict['functions']]))
        got_functions = list(set([x['function'] for x in functions]))
        if (condition_functions != got_functions) and (len(condition_functions) < len(got_functions)):
            msg = colored(f"You added more functions in graded cell {cell_number}. Autograder will likely fail.\n", 'red')
            added_functions = [x for x in got_functions if x not in condition_functions]
            msg += f"Added functions: {added_functions}.\n"
            msg += f"Expected functions: {condition_functions}"
            return False, msg
        if (condition_functions != got_functions) and (len(condition_functions) > len(got_functions)):
            msg = colored(f"You removed some functions in graded cell {cell_number}. Check if you haven't added them in another cell. Autograder will likely fail.\n",'red')
            removed_functions = [x for x in condition_functions if x not in got_functions]
            msg += f"Functions removed: {removed_functions}."
            return False, msg
        if (condition_functions != got_functions) and (len(condition_functions) == len(got_functions)):
            msg = colored(f"Different set of functions than expected in graded cell number {cell_number}. Make sure you haven't moved any function in the graded cell to another one.", 'red')
            msg += f"Expected functions: {condition_functions}.\nGot functions: {got_functions}."
            return False, msg
        for function in condition_functions:
            condition_args = [x['args']['arg_names'] for x in conditions_dict['functions'] if x['function'] == function][0]
            got_args = [x['args']['arg_names'] for x in functions if x['function'] == function][0]
            if condition_args != got_args:
                msg = colored(f"Arguments in function {function} in graded cell number {cell_number} have been changed. Autograder will likely fail.\n", 'red')
                msg += f"Expected arguments: {condition_args}.\n"
                msg += f"Got arguments: {got_args}."
                return False, msg
            if [x['args']['has_non_constant_args'] for x in functions if x['function'] == function][0]:
                msg = colored(f"Function {function} has non constant args (arguments that points to an object in the jupyter notebook) in graded cell number {cell_number}. Autograder will likely fail.\n", 'red')
                return False, msg
            #got_has_return = [x['has_return'] for x in functions if x['function']==function][0]
            #condition_has_return = [x['has_return'] for x in conditions_dict['functions'] if x['function']==function][0]
            #if got_has_return != condition_has_return:
            #    if got_has_return == True:
            #        msg = colored(f"Function {function} in cell number {cell_number} has a return statement when it shouldn't have. Autograder will likely fail.", 'red')
            #    elif got_has_return == False:
            #        msg = colored(f"Function {function} in cell number {cell_number} hasn't a return statement whtn it should have. Autograder will likely fail.", 'red')
            #    return False, msg
        
    if (classes is not None) and conditions_dict['has_classes']:
        condition_classes = list(set([x['name'] for x in conditions_dict['classes']]))
        got_classes= list(set([x['name'] for x in classes]))
        if condition_classes != got_classes:
            msg = colored(f"There are extra or missing classes in cell number {cell_number}. Autograder will likely fail.\n", 'r')
            msg += f"Expected classes: {condition_classes}.\n"
            msg += f"Got classes: {got_classes}"
            return False, msg
        for class_ in condition_classes:
            condition_methods = [x['methods'] for x in conditions_dict['classes'] if x['name'] == class_][0]
            got_methods = [x['methods'] for x in classes if x['name'] == class_][0]
            condition_function_names = list(set([x['function'] for x in condition_methods]))
            got_function_names = list(set([x['function'] for x in got_methods]))
            if condition_function_names != got_function_names:
                msg = colored(f"Incorrect methods for class {class_} in cell number {cell_number}. You should not change any given class method. Autograder will likely fail.\n", 'red')
                msg += f"Expected: {condition_function_names}.\n"
                msg += f"Got: {got_function_names}."
                return False, msg
            

    return True, colored("All checks are ok! If you passed all unittests, your submission is likely to pass the autograder.", 'green')


def check_notebook():
    nb = load_nb(path)
    passed, graded_cells = get_graded_cells(nb, CONDITIONS_DICT)
    analyzed_cells = []
    if not passed and passed is not None:
        return print(graded_cells)
    else:
        for i, graded_cell in enumerate(graded_cells):
            tree, code = parse_graded_cell(graded_cell)
            analyzed_cells.append(cell_checker(tree, code, i + 1 - GRADED_SHIFT, CONDITIONS_DICT[i]))

    approved = [y for x,y in analyzed_cells if x == True]
    reproved = [y for x,y in analyzed_cells if x == False]
    if len(reproved) == 0:
        print(approved[0])
    else:
        for feedback in reproved:
            print(feedback)
            print("\n")

        
        


def gen_graded_cells_info(path):
    nb = load_nb(path)
    condition_dicts = []
    passed, graded_cells = get_graded_cells(nb)
    for i, graded_cell in enumerate(graded_cells):
        tree,code = parse_graded_cell(graded_cell)
        graded_tree = GradedTree(tree)
        condition_dict = graded_tree.gen_conditions_dict(i)
        condition_dicts.append(condition_dict)
    return condition_dicts

        

import re
import sys

def tokenize(code):
    tokens = []
    token_specification = [
        ('INTEGER', r'INTEGER'),               # INTEGER keyword
        ('PRINT', r'PRINT'),                   # PRINT keyword
        ('COMMA', r','),                       # Comma for PRINT statements
        ('ASTERISK', r'\*'),                   # Asterisk for PRINT statements
        ('IF', r'IF'),                         # IF keyword
        ('THEN', r'THEN'),                     # THEN keyword
        ('DO', r'DO'),                         # DO keyword
        ('END_IF', r'END IF'),                 # END IF keyword
        ('END_DO', r'END DO'),                 # END DO keyword
        ('DOUBLE_COLON', r'::'),               # Double colon
        ('STRING', r'"[^"]*"'),                # String literals
        ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),    # Identifiers
        ('NUMBER', r'\d+(\.\d*)?'),            # Numbers
        ('ASSIGN', r'='),                      # Assignment
        ('RELOP', r'(<=|>=|==|<|>|/=)'),      # Relational operators
        ('LPAREN', r'\('),                     # Left parenthesis
        ('RPAREN', r'\)'),                     # Right parenthesis
        ('NEWLINE', r'\n'),                    # Line endings
        ('SKIP', r'[ \t]+'),                   # Whitespace
        ('MISMATCH', r'.'),                    # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'STRING':
            value = value.strip('"')
        elif kind == 'NEWLINE':
            line_num += 1
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character "{value}" at line {line_num}')
        tokens.append((kind, value))
    return tokens

class PrintNode:
    def __init__(self, values):
        self.values = values

class AssignmentNode:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

class IfNode:
    def __init__(self, condition, then_statements):
        self.condition = condition
        self.then_statements = then_statements

class DoNode:
    def __init__(self, variable, start, end, body_statements):
        self.variable = variable
        self.start = start
        self.end = end
        self.body_statements = body_statements

def parse_print_statement(tokens, i):
    values = []
    i += 1  # Skip PRINT
    if i < len(tokens) and tokens[i][0] == 'ASTERISK':
        i += 1
    if i < len(tokens) and tokens[i][0] == 'COMMA':
        i += 1
    
    while i < len(tokens) and tokens[i][0] != 'NEWLINE':
        if tokens[i][0] != 'COMMA':
            if tokens[i][0] == 'STRING':
                values.append(tokens[i][1])
            elif tokens[i][0] == 'ID':
                values.append(('var', tokens[i][1]))
            else:
                values.append(str(tokens[i][1]))
        i += 1
    return PrintNode(values), i

def parse(tokens):
    ast = []
    i = 0
    while i < len(tokens):
        if i >= len(tokens):
            break
            
        token, value = tokens[i]

        if token == 'INTEGER':
            i += 1  # Move to the double colon
            if tokens[i][0] == 'DOUBLE_COLON':
                i += 1  # Move to the variable name
                var_token, var_name = tokens[i]
                if var_token == 'ID':
                    ast.append(AssignmentNode(var_name, 0))

        elif token == 'ID':
            var_name = value
            i += 1  # Move to assignment operator
            if i < len(tokens) and tokens[i][0] == 'ASSIGN':
                i += 1  # Move to the value being assigned
                expr_token, expr_value = tokens[i]
                ast.append(AssignmentNode(var_name, expr_value))

        elif token == 'PRINT':
            node, i = parse_print_statement(tokens, i)
            ast.append(node)
            continue

        elif token == 'IF':
            i += 1  # Skip IF
            condition = []
            while i < len(tokens) and tokens[i][0] != 'THEN':
                if tokens[i][0] not in ['NEWLINE']:
                    condition.append(str(tokens[i][1]))
                i += 1
            i += 1  # Skip THEN
            
            then_statements = []
            while i < len(tokens):
                if tokens[i][0] == 'END_IF':
                    break
                if tokens[i][0] == 'PRINT':
                    node, i = parse_print_statement(tokens, i)
                    then_statements.append(node)
                else:
                    i += 1
            
            ast.append(IfNode(' '.join(condition), then_statements))
            i += 1  # Skip END IF

        elif token == 'DO':
            i += 1  # Move to loop variable
            loop_var = tokens[i][1]
            i += 2  # Skip to start value
            start_value = tokens[i][1]
            i += 2  # Skip to end value
            end_value = tokens[i][1]
            i += 1  # Move past end value
            
            body_statements = []
            while i < len(tokens):
                if tokens[i][0] == 'END_DO':
                    break
                if tokens[i][0] == 'PRINT':
                    node, i = parse_print_statement(tokens, i)
                    body_statements.append(node)
                else:
                    i += 1
            
            ast.append(DoNode(loop_var, start_value, end_value, body_statements))
            i += 1  # Skip END DO

        i += 1
    return ast

def format_print_values(values):
    formatted = []
    for value in values:
        if isinstance(value, tuple) and value[0] == 'var':
            formatted.append(value[1])  # Variable name without quotes
        else:
            formatted.append(repr(str(value)))  # String literals with quotes
    return ', '.join(formatted)

def transpile(ast):
    js_code = "// Generated from FORTRAN source\n\n"
    
    # Add helper function for DO loops with proper FORTRAN semantics
    js_code += """function doLoop(init, final, step, callback) {
    // Ensure FORTRAN DO loop semantics with at least one iteration
    let index = init;
    if (step > 0 && index <= final) {
        do {
            callback(index);
            index += step;
        } while (index <= final);
    } else if (step < 0 && index >= final) {
        do {
            callback(index);
            index += step;
        } while (index >= final);
    } else if (init === final) {
        // Execute exactly once when init equals final
        callback(init);
    }
}

"""
    # Track declared variables to avoid duplicate declarations
    declared_vars = set()
    
    for node in ast:
        if isinstance(node, AssignmentNode):
            if node.variable not in declared_vars:
                js_code += f"let {node.variable} = {node.value};\n"
                declared_vars.add(node.variable)
            else:
                js_code += f"{node.variable} = {node.value};\n"
        elif isinstance(node, PrintNode):
            js_code += f"console.log({format_print_values(node.values)});\n"
        elif isinstance(node, IfNode):
            condition = node.condition.replace('/=', '!=').replace('.EQ.', '===').replace('.NE.', '!==')
            js_code += f"if ({condition}) {{\n"
            for statement in node.then_statements:
                js_code += f"    console.log({format_print_values(statement.values)});\n"
            js_code += "}\n"
        elif isinstance(node, DoNode):
            js_code += f"doLoop({node.start}, {node.end}, 1, ({node.variable}) => {{\n"
            for statement in node.body_statements:
                js_code += f"    console.log({format_print_values(statement.values)});\n"
            js_code += "});\n"
    return js_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python transpiler.py <file.f90s or file.f70s>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith(('.f90s', '.f70s')):
        print("Error: Input file must have a .f90s or .f70s extension.")
        sys.exit(1)

    output_filename = filename.rsplit('.', 1)[0] + '.js'

    try:
        with open(filename, 'r') as file:
            code = file.read()

        tokens = tokenize(code)
        ast = parse(tokens)
        js_code = transpile(ast)

        with open(output_filename, 'w') as output_file:
            output_file.write(js_code)

        print(f"JavaScript code generated and saved to {output_filename}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

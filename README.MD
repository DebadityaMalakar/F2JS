# FORTRAN-Like to JavaScript Transpiler Cheatsheet

## Overview
This project is a transpiler that converts code written in a FORTRAN-like syntax (with extensions `.f90s` or `.f70s`) into JavaScript. It supports basic control structures such as assignment, printing, conditionals, and loops.

## Features
- **Tokenization**: Converts source code into tokens.
- **Parsing**: Constructs an Abstract Syntax Tree (AST) from the tokens.
- **Transpilation**: Converts the AST into equivalent JavaScript code.
- **Support for**:
  - Variable declaration and assignment
  - `PRINT` statements
  - Conditional statements (`IF...THEN...END IF`)
  - Loop statements (`DO...END DO`)

## Installation
1. Ensure you have Python installed on your system.
2. Clone the repository or download the transpiler code.
3. Save the code into a file named `transpiler.py`.

## Usage
1. **Create a FORTRAN-like source file**: Create a file with a `.f90s` or `.f70s` extension. Below is an example:
    ```fortran
    INTEGER :: myVar
    myVar = 5
    PRINT *, "The value is", myVar

    IF myVar > 0 THEN
        PRINT *, "Positive"
    END IF

    DO i = 1, 5
        PRINT *, "Count:", i
    END DO
    ```

2. **Run the transpiler**: Open your terminal and run the following command:
    ```bash
    python transpiler.py your_file.f90s
    ```
    Replace `your_file.f90s` with the path to your source file.

3. **Output**: The transpiler will generate a JavaScript file with the same base name as the input file but with a `.js` extension. For example, `your_file.js`.

## File Extensions
- **Input**: `.f90s`, `.f70s` (FORTRAN-like syntax)
- **Output**: `.js` (JavaScript code)

## Error Handling
- The transpiler checks for invalid input files and raises errors for unexpected characters or mismatched structures in the source code.

## Example of Transpilation
Given the input:
```fortran
INTEGER :: x
x = 10
PRINT *, "Value of x is", x
IF x > 5 THEN
    PRINT *, "x is greater than 5"
END IF

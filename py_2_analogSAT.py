#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 10:56:50 2024
Modified on Thu Nov  14

@author: chunchic
"""



# Path to the CNF file
input_file = 'problem.cnf'

# Initialize a list to hold all clauses
clauses = []

# Open the file and read lines
with open(input_file, 'r') as file1:
    for line in file1:
        # Strip whitespace from the start and end of the line
        cleaned_line = line.strip()
        # Skip lines that start with 'c' or are empty
        if cleaned_line.startswith('c') or not cleaned_line:
            continue
        if cleaned_line.startswith('p'):
            n = int(cleaned_line.split()[2])
            n_clause = int(cleaned_line.split()[3])
            continue
        # Split the line into parts and convert them to integers, ignoring the last element '0'
        clause = [int(x) for x in cleaned_line.split()[:-1]]
        # Add the clause to the list of clauses
        clauses.append(clause)

# Removing any empty clauses if input file has empty lines
clauses = [clause for clause in clauses if clause]

# Generating netlist
lines = []

# Defining control circuitry
lines.append("* Control circuit\n")
lines.append("ESAT1 contra 0 value={fsat1()}\n")
lines.append("RSAT1 contra 0 100meg\n")
lines.append("ESAT2 contrd 0 value={fsat2()}\n")
lines.append("RSAT2 contrd 0 100meg\n")
lines.append("\n")

# Integrators for the main variables
lines.append("* Main variables\n")
for i in range(1,n+1):
    lines.append(f"Cs{i} s{i} 0 1 IC={{-1+mc(1,1)}}\n")
    lines.append(f"Gs{i} 0 s{i} value={{fs{i}()}}\n")
    lines.append(f"Rs{i} s{i} 0 100meg\n")   
lines.append("\n")          
    
# Integrators for the auxiliary variables
lines.append("* Memory variables\n")
for i in range(1,n_clause+1):
    lines.append(f"Ca{i} a{i} 0 1 IC={{1}}\n")
    lines.append(f"Ga{i} 0 a{i} value={{fa{i}()}}\n")
    lines.append(f"Ra{i} a{i} 0 100meg\n")
lines.append("\n")

# Clause functions
lines.append("* functions\n")
lines.append(".func Cm(x,y,z)={0.5*min(1-x,min(1-y,1-z))}\n")
lines.append(".func Cm1(x,y,z)={min(1-u(x),min(1-u(y),1-u(z)))}\n")
lines.append("\n")

# Sum of clauses
fsat1_line = ".func fsat1()="
fsat2_line = ".func fsat2()="
for i in range(n_clause):
    fsat1_line += "Cm("
    fsat2_line += "Cm1("
    s = clauses[i]
    for j in range(3):
        if s[j] < 0:
            fsat1_line += "-"
            fsat2_line += "-" 
        fsat1_line += f"V(s{abs(s[j])}),"
        fsat2_line += f"V(s{abs(s[j])}),"
    fsat1_line = fsat1_line[:-1] # removing an extra coma
    fsat2_line = fsat2_line[:-1]
    fsat1_line += ")+"
    fsat2_line += ")+"
fsat1_line = fsat1_line[:-1] # removing an extra plus
fsat2_line = fsat2_line[:-1]
fsat1_line += "\n"
fsat2_line += "\n"

lines.append(fsat1_line)
lines.append("\n")    
lines.append(fsat2_line)
lines.append("\n")  

# Evolution functions for the main variables
abs_clauses = [[abs(i) for i in clause] for clause in clauses]
for i in range(n):
    # Finding all clauses where variable i appears
    tmp = []
    for j_index, clause in enumerate(abs_clauses):
        if i+1 in clause:
            tmp.append(j_index)
    
    # Generating the evolution function
    fs_line = f".func fs{i+1}() = {{"
    for j in tmp:
        # the other two variables in clause
        tmp2 = [k for k in clauses[j] if k != i+1 and k != -(i+1)]
        
        # lines for K
        if i+1 in clauses[j]:
            var_sign = "*(1)"
        else:
            var_sign = "*(-1)"       
        pow_line = ""    
        for k in range(3):
            # power 1 if index i in clause, power 2 for the other two indexes in clause
            if abs(clauses[j][k]) == i+1:
                pow_digit = "1"
            else:
                pow_digit = "2"
            if clauses[j][k] >= 0:
                pow_line += f"*pow(1-V(s{abs(clauses[j][k])})," + pow_digit + ")" 
            else:
                pow_line += f"*pow(1+V(s{abs(clauses[j][k])})," + pow_digit + ")" 
                
        fs_line += f"2*V(a{j+1})" + var_sign + pow_line + "+"     
    fs_line = fs_line[:-1] # remove an extra plus
    fs_line += "}\n"
    lines.append(fs_line)
lines.append("\n")

# Evolution functions for the auxiliary variables
for i in range(n_clause):
    # checking negations
    s_sign = []
    for j in range(3):
        # opposite sign here
        if clauses[i][j] / abs_clauses[i][j] == 1:
            s_sign.append("-")
        else:
            s_sign.append("+")
    fa_line = f".func fa{i+1}() = {{V(a{i+1})*pow((1" + s_sign[0] + f"V(s{abs_clauses[i][0]}))*(1" + s_sign[1] + f"V(s{abs_clauses[i][1]}))*(1" + s_sign[2] + f"V(s{abs_clauses[i][2]})),2)}}\n"
    lines.append(fa_line)
lines.append("\n")
lines.append("\n")

# Transient simulation command
lines.append(".tran 0 300.000000 1u uic\n")
lines.append("\n")
probe_line = ".probe V(contra) V(contrd)"
for i in range(n):
    probe_line += f" V(s{i+1})"
lines.append(probe_line)

# Saving the netlist
output_file = input_file + '.py.analogSAT.net'
with open(output_file, 'w') as file2:
    file2.writelines(lines)

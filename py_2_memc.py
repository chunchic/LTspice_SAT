#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 10:56:50 2024
Modified on Thu Nov  15

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
lines.append("* parameters\n");
lines.append(f".param alpha=5.000000 beta=20.000000 gamma=0.250000 delta=0.050000 epsilon=0.001000 xi=0.010000 xlmax={len(clauses)*10000}\n")
lines.append("\n")

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
    lines.append(f"Cv{i} v{i} 0 1 IC={{-1+mc(1,1)}}\n")
    lines.append(f"Gv{i} 0 v{i} value={{fv{i}()*(u(1-V(v{i}))*u(fv{i}())+u(V(v{i})+1)*u(-fv{i}()))}}\n")
    lines.append(f"Rv{i} v{i} 0 100meg\n")   
lines.append("\n")          
    
# Integrators for the short memory variables
lines.append("* Short memory variables\n")
for i in range(1,n_clause+1):
    lines.append(f"Cs{i} xs{i} 0 1 IC={{0.5}}\n")
    lines.append(f"Gs{i} 0 xs{i} value={{fs{i}()*(u(1-V(xs{i}))*u(fs{i}())+u(V(xs{i}))*u(-fs{i}()))}}\n")
    lines.append(f"Rs{i} xs{i} 0 100meg\n")
lines.append("\n")

# Integrators for the long memory variables
lines.append("* Long memory variables\n")
for i in range(1,n_clause+1):
    lines.append(f"Cl{i} xl{i} 0 1 IC={{1}}\n")
    lines.append(f"Gl{i} 0 xl{i} value={{fl{i}()*(u(xlmax-V(xl{i}))*u(fl{i}())+u(V(xl{i})-1)*u(-fl{i}()))}}\n")
    lines.append(f"Rl{i} xl{i} 0 100meg\n")
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
    v = clauses[i]
    for j in range(3):
        if v[j] < 0:
            fsat1_line += "-"
            fsat2_line += "-" 
        fsat1_line += f"V(v{abs(v[j])}),"
        fsat2_line += f"V(v{abs(v[j])}),"
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
    fv_line = f".func fv{i+1}() = {{"
    for j in tmp:
        # the other two variables in clause
        tmp2 = [k for k in clauses[j] if k != i+1 and k != -(i+1)]
        # lines for G
        if tmp2[0] >= 0:
            G1_line = f"1-V(v{abs(tmp2[0])})"
            var1_sign = f"V(v{abs(tmp2[0])})"
        else:
            G1_line = f"1+V(v{abs(tmp2[0])})"
            var1_sign = f"-V(v{abs(tmp2[0])})"
        if tmp2[1] >= 0:
            G2_line = f"1-V(v{abs(tmp2[1])})"
            var2_sign = f"V(v{abs(tmp2[1])})"
        else:
            G2_line = f"1+V(v{abs(tmp2[1])})"
            var2_sign = f"-V(v{abs(tmp2[1])})"
        # lines for R
        if i+1 in clauses[j]:
            R_line = f"(1-V(v{i+1}))"
            var_sign = f"V(v{i+1})"
            point_five = "0.5"
        else:
            R_line = f"(-1-V(v{i+1}))"
            var_sign = f"-V(v{i+1})"
            point_five = "(-0.5)"
        fv_line += f"V(xl{j+1})*V(xs{j+1})*" + point_five + "*min(" + G1_line + "," + G2_line + f")+(1+xi*V(xl{j+1}))*(1-V(xs{j+1}))*0.5*" + R_line + "*" + "if(" + var_sign + " > " + var1_sign + ", if(" + var_sign + " > " + var2_sign + ",1,0),0)+"
    fv_line = fv_line[:-1] # remove an extra plus
    fv_line += "}\n"
    lines.append(fv_line)
lines.append("\n")

# Evolution functions for the short and long memory variables
tmp_lines = []
for i in range(n_clause):
    # checking negations
    v_sign = []
    for j in range(3):
        if clauses[i][j] / abs_clauses[i][j] == 1:
            v_sign.append("")
        else:
            v_sign.append("-")
    fs_line = f".func fs{i+1}() = {{beta*(V(xs{i+1})+epsilon)*(Cm(" + v_sign[0] + f"V(v{abs_clauses[i][0]})," + v_sign[1] + f"V(v{abs_clauses[i][1]})," + v_sign[2] + f"V(v{abs_clauses[i][2]}))-gamma)}}\n"
    fl_line = f".func fl{i+1}() = {{alpha*(Cm(" + v_sign[0] + f"V(v{abs_clauses[i][0]})," + v_sign[1] + f"V(v{abs_clauses[i][1]})," + v_sign[2] + f"V(v{abs_clauses[i][2]}))-delta)}}\n"
    lines.append(fs_line)
    tmp_lines.append(fl_line)
lines.append("\n")
lines.extend(tmp_lines)
lines.append("\n")

# Transient simulation command
lines.append(".tran 0 300.000000 1u uic\n")
lines.append("\n")
probe_line = ".probe V(contra) V(contrd)"
for i in range(n):
    probe_line += f" V(v{i+1})"
lines.append(probe_line)

# Saving the netlist
output_file = input_file + '.py.memc.net'
with open(output_file, 'w') as file2:
    file2.writelines(lines)


This project provides a Python script that reads a .cnf file containing a 3-SAT instance and converts it into a .net file for simulation in LTspice using memcomputing and AnalogSAT equations. 

The goal is to enable users to simulate 3-SAT problems with LTspice circuits that emulate memcomputing architectures, facilitating exploration of potential hardware solutions for NP-hard problems.

Features

Input: Reads a .cnf file containing a 3-SAT problem in standard DIMACS format.

Output: Generates a corresponding .net file for LTspice that simulates the clauses and variables as memcomputing circuits.

Prerequisites

Python 3.x: The script is written in Python and requires a standard Python installation.

LTspice: For simulating the generated .net file.

Usage

Run the script with the following command:

python py_2_analogSAT.py

python py_2_memc.py




CNF Format

The input .cnf file should follow the DIMACS format, which is standard for 3-SAT problems:

Each line represents a clause with integers.

Variables are represented as positive integers.

Negated variables are represented as negative integers.

Each clause ends with a 0.

The header line starts with p cnf followed by the number of variables and clauses.

Example of CNF file

p cnf 3 4

1 -3 2 0

-1 2 3 0

1 -2 -3 0

-1 -2 3 0

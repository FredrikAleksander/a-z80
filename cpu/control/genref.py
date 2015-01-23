#!/usr/bin/env python
#
# This script reads and parses selected Verilog and SystemVerilog modules
# and generates a set of Verilog include files for the control block.
#
#-------------------------------------------------------------------------------
#  Copyright (C) 2014  Goran Devic
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#-------------------------------------------------------------------------------
import glob
import os

with open('../top-level-files.txt') as f:
    files = f.read().splitlines()

# Create 2 files that should be included in the execution engine block:
# 1. A module arguments section
# 2. A file containing the code to initialize control wires to zero
with open('exec_module.vh', 'w') as file1, open('exec_zero.vh', 'w') as file0:
    file1.write("// Automatically generated by genref.py\n")
    file0.write("// Automatically generated by genref.py\n")

# Read and parse each file from the list of input files
for infile in files:
    wires = []
    if not os.path.isfile('../' + infile):
        continue
    with open('../' + infile, "r") as f:
        for line in f:
            info = line.split()
            # input wire register case
            if len(info)>2 and info[0]=="input" and info[1]=="wire" and info[2].startswith("ctl_"):
                wires.append(info[2].translate(None, ';,'))
            # input wire [1:0] bus case
            if len(info)>3 and info[0]=="input" and info[1]=="wire" and info[2].startswith("[") and info[3].startswith("ctl_"):
                wires.append(info[2] + " " + info[3].translate(None, ';,'))

    if len(wires)>0:
        with open('exec_module.vh', 'a') as file1, open('exec_zero.vh', 'a') as file0:
            print "MODULE: " + infile
            file0.write("\n// Module: " + infile + "\n")
            file1.write("\n// Module: " + infile + "\n")
            for wire in wires:
                print "   " + wire
                file1.write("output logic " + wire + ",\n")
                # To the exec include, write bus with the length field (if the wire is a bus)
                # To the zero include, skip bus width field
                if "[" in wire:
                    file0.write(wire.split()[1] + " = 0;\n")
                else:
                    file0.write(wire + " = 0;\n")                    

# Touch a file that includes 'exec_module.vh' and 'exec_zero.vh' to ensure it will recompile correctly
os.utime("execute.sv", None)

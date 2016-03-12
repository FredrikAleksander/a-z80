#!/usr/bin/env python3
#
# This script reads and parses selected Verilog and SystemVerilog modules
# and generates a set of Verilog include files for the Z80 top-level block.
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
import os

with open('../top-level-files.txt') as f:
    files = f.read().splitlines()

# Create a file that should be included in the top-level source
with open('globals.vh', 'w') as file1:
    file1.write("// Automatically generated by genglobals.py\n")

# Keep track of duplicated symbols across all files
globals = []

# Read and parse each file from the list of input files
for infile in files:
    wires = []
    if not os.path.isfile('../' + infile):
        continue
    with open('../' + infile, "r") as f:
        for line in f:
            info = line.split()
            if len(info)>2:
                # There can be only one driver for each signal so we read only the outputs
                if info[0]=="output" and (info[1]=="wire" or info[1]=="reg" or info[1]=="logic"):
                    # There are 2 cases: wires and buses
                    if info[2].startswith('['):
                        wires.append(info[2] + ' ' + info[3].strip(';,'))
                    else:
                        wires.append(info[2].strip(';,'))

    if len(wires)>0:
        with open('globals.vh', 'a') as file1:
            file1.write("\n// Module: " + infile + "\n")
            for wire in wires:
                # Everything in globals is a wire
                # (Can't use 'logic' since some buses are bidirectional)
                if wire in globals:
                    file1.write("// wire " + wire + "; (previously defined)\n")
                else:
                    file1.write("wire " + wire + ";\n")
                    globals.append(wire)

# Touch files that include 'globals.vh' to ensure it will recompile correctly
os.utime("core.vh", None)
os.utime("z80_top_direct_n.v", None)
os.utime("z80_top_ifc_n.sv", None)

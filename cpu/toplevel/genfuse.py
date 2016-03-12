#!/usr/bin/env python3
#
# This script generates a test include file from a set of "Fuse" test vectors.
#
# Three common testing configurations are:
#
# 1. You want to test a specific instruction only, say 02 LD (BC),A (see Fuse tests.in)
#    start_test = "02"
#    run_tests = 1
#    regress = 0
#
# 2. You want to run a smaller subset of 'regression' tests:
#    start_test = "00"
#    run_tests = 1
#    regress = 1
#
# 3. You want to run a full Fuse test suite (all instructions!):
#    start_test = "00"
#    run_tests = -1
#    regress = 0
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

# Start with this test name (this is a string; see tests files)
start_test = "00"

# Number of tests to run; use -1 to run all tests
run_tests = 1

# Set this to 1 to use regression test files instead of 'tests.*'
# It will run all regression tests (start_test, run_tests are ignored)
regress = 1

#------------------------------------------------------------------------------
# Determine which test files to use
tests_in = 'fuse/tests.in'
tests_expected = 'fuse/tests.expected'

# Regression testing executes all regression tests
if regress:
    tests_in = 'fuse/regress.in'
    tests_expected = 'fuse/regress.expected'
    start_test = "00"
    run_tests = -1

with open(tests_in) as f1:
    t1 = f1.read().splitlines()
# Remove all tests until the one we need to start with. Tests are separated by empty lines.
while t1[0].split(" ")[0]!=start_test:
    while len(t1.pop(0))>0:
        pass
t1 = list(filter(None, t1)) # Filter out empty lines

with open(tests_expected) as f2:
    t2 = f2.read().splitlines()
while t2[0].split(" ")[0]!=start_test:
    while len(t2.pop(0))>0:
        pass

# Count total clocks required to run all selected tests
total_clks = 0

def RegWrite(reg, hex):
    global total_clks
    ftest.write("   // Preset " + reg + "\n")
    ftest.write("   force dut.reg_file_.b2v_latch_" + reg + "_lo.we=1;\n")
    ftest.write("   force dut.reg_file_.b2v_latch_" + reg + "_hi.we=1;\n")
    ftest.write("   force dut.reg_file_.b2v_latch_" + reg + "_lo.db=8'h" + hex[2:] + ";\n")
    ftest.write("   force dut.reg_file_.b2v_latch_" + reg + "_hi.db=8'h" + hex[0:2] + ";\n")
    ftest.write("#2 release dut.reg_file_.b2v_latch_" + reg + "_lo.we;\n")
    ftest.write("   release dut.reg_file_.b2v_latch_" + reg + "_hi.we;\n")
    ftest.write("   release dut.reg_file_.b2v_latch_" + reg + "_lo.db;\n")
    ftest.write("   release dut.reg_file_.b2v_latch_" + reg + "_hi.db;\n")
    total_clks = total_clks + 2

def RegRead(reg, hex):
    ftest.write("   if (dut.reg_file_.b2v_latch_" + reg + "_lo.latch!==8'h" + hex[2:] +  ") $fdisplay(f,\"* Reg " + reg + " " + reg[1] + "=%h !=" + hex[2:] +  "\",dut.reg_file_.b2v_latch_" + reg + "_lo.latch);\n")
    ftest.write("   if (dut.reg_file_.b2v_latch_" + reg + "_hi.latch!==8'h" + hex[0:2] + ") $fdisplay(f,\"* Reg " + reg + " " + reg[0] + "=%h !=" + hex[0:2] + "\",dut.reg_file_.b2v_latch_" + reg + "_hi.latch);\n")

#---------------------------- START -----------------------------------
# Create a file that should be included in the test_fuse source
ftest = open('test_fuse.vh', 'w')
ftest.write("// Automatically generated by genfuse.py\n\n")

# Initial pre-test state is reset and control signals asserted
ftest.write("force dut.resets_.clrpc=0;\n")
ftest.write("force dut.reg_file_.reg_gp_we=0;\n")
ftest.write("force dut.reg_control_.ctl_reg_sys_we=0;\n")
ftest.write("force dut.z80_top_ifc_n.fpga_reset=1;\n")
ftest.write("#2\n")
total_clks = total_clks + 2

# Read each test from the testdat.in file
while True:
    ftest.write("//" + "-" * 80 + "\n")
    if len(t1)==0 or run_tests==0:
        break
    run_tests = run_tests-1

    # Clear opcode register before starting a new instruction
    ftest.write("   force dut.ir_.ctl_ir_we=1;\n")
    ftest.write("   force dut.ir_.db=0;\n")
    ftest.write("#2 release dut.ir_.ctl_ir_we;\n")
    ftest.write("   release dut.ir_.db;\n")
    total_clks = total_clks + 2

    # Format of the test.in file:
    # <arbitrary test description>
    # AF BC DE HL AF' BC' DE' HL' IX IY SP PC
    # I R IFF1 IFF2 IM <halted> <tstates>
    name = t1.pop(0)
    ftest.write("$fdisplay(f,\"Testing opcode " + name + "\");\n")
    name = name.split(" ")[0]
    r = t1.pop(0).split(' ')
    r = list(filter(None, r))
    # 0  1  2  3  4   5   6   7   8  9  10 11   (index)
    # AF BC DE HL AF' BC' DE' HL' IX IY SP PC
    RegWrite("af", r[0])
    RegWrite("bc", r[1])
    RegWrite("de", r[2])
    RegWrite("hl", r[3])
    RegWrite("af2", r[4])
    RegWrite("bc2", r[5])
    RegWrite("de2", r[6])
    RegWrite("hl2", r[7])
    RegWrite("ix", r[8])
    RegWrite("iy", r[9])
    RegWrite("sp", r[10])
    RegWrite("wz", "0000")       # Initialize WZ with 0
    RegWrite("pc", r[11])

    s = t1.pop(0).split(' ')
    s = list(filter(None, s))
    # 0 1 2    3    4  5        6          (index)
    # I R IFF1 IFF2 IM <halted> <tstates?>
    RegWrite("ir", s[0]+s[1])
    # TODO: Store IFF1/IFF2, IM, in_halt

    # Read memory configuration from the test.in until the line contains only -1
    while True:
        m = t1.pop(0).split(' ')
        if m[0]=="-1":
            break
        address = int(m.pop(0),16)
        ftest.write("   // Preset memory\n")
        while True:
            d = m.pop(0)
            if d=="-1":
                break
            ftest.write("   ram.Mem[" + str(address) + "] = 8'h" + d + ";\n")
            address = address+1

    # We need to prepare the IO map to be able to handle IN/OUT instructions.
    # Copy tests.out (so we don't modify it just yet), parse all PR and PW (port read, write)
    # statements and then fill in our IO map (for IO reads) or stack the check statements to be
    # used below after the opcode has executed (for IO writes)
    check_io = []               # List of check statements (for OUT instructions)
    t2b = list(t2)
    while True:
        m = t2b.pop(0).split(' ')
        m = list(filter(None, m))
        if len(m)==0 or m[0]=="-1":
            break
        if len(m)==4 and m[1]=="PR":
            address = int(m[2],16)
            ftest.write("   io.IO[" + str(address) + "] = 8'h" + m[3] + ";\n")
        if len(m)==4 and m[1]=="PW":
            address = int(m[2],16)
            check_io.append("   if (io.IO[" + str(address) + "]!==8'h" + m[3] + ") $fdisplay(f,\"* IO[" + hex(address)[2:] + "]=%h !=" + m[3] + "\",io.IO[" + str(address) + "]);\n")

    # Prepare instruction to be run. By releasing the fpga_reset, internal CPU reset will be active for 1T.
    # Due to the instruction execution overlap, first 2T of an instruction may be writing
    # value back to a general purpose register (like AF) and we need to prevent that.
    # Similarly, we let the execution continues 2T into the next instruction but we prevent
    # it from writing to system registers so it cannot update PC and IR.
    ftest.write("   force dut.z80_top_ifc_n.fpga_reset=0;\n")
    ftest.write("   force dut.address_latch_.Q=16'h" + r[11] +";\n") # Force PC into the address latch
    ftest.write("   release dut.reg_control_.ctl_reg_sys_we;\n")
    ftest.write("   release dut.reg_file_.reg_gp_we;\n")
    ftest.write("#3\n")             # 1T (#2) overlaps the reset cycle
    total_clks = total_clks + 3     # We borrow 1T (#2) to to force the PC to be what our test wants...
    ftest.write("   release dut.address_latch_.Q;\n")
    ftest.write("#1\n")
    total_clks = total_clks + 1

    # Read and parse the tests expected list which contains the expected results of our run,
    # including the number of clocks for a particular instruction
    xname = t2.pop(0).split()[0]
    if name!=xname:
        print("Test " + name + " does not correspond to test.expected " + xname)
        break
    # Skip the memory access logs; read to the expected register content list
    while True:
        l = t2.pop(0)
        if l[0]!=' ':
            break
    r = l.split(' ')
    r = list(filter(None, r))

    s = t2.pop(0).split(' ')
    s = list(filter(None, s))

    ticks = int(s[6]) * 2 - 2       # We return 1T (#2) that we borrowed to set PC
    total_clks = total_clks + ticks
    ftest.write("#" + str(ticks) + " // Execute\n")

    ftest.write("   force dut.reg_control_.ctl_reg_sys_we=0;\n")
    ftest.write("#2 pc=z.A;\n")     # Extra 2T for the next instruction overlap & read PC on the ABus
    ftest.write("#2\n")             # Complete this instruction
    ftest.write("#1 force dut.reg_file_.reg_gp_we=0;\n")    # Add 1/2 clock for any pending flops to latch (mainly the F register)
    ftest.write("   force dut.z80_top_ifc_n.fpga_reset=1;\n")
    total_clks = total_clks + 5

    # Now we can issue register reading commands
    # We are guided on what to read and check by the content of "test.expected" file

    # Special case are the register exchange instructions and there are 3 of them.
    # The exchange operations are not tested directly; instead, the latches that control register bank access are
    if xname=="08":                 # EX AF,AF1
        r[0],r[4] = r[4],r[0]
        ftest.write("   if (dut.reg_control_.bank_af!==1) $fdisplay(f,\"* Bank AF!=1\");\n")
    if xname=="eb":                 # EX DE,HL
        r[2],r[3] = r[3],r[2]
        ftest.write("   if (dut.reg_control_.bank_hl_de1!==1) $fdisplay(f,\"* Bank HL/DE!=1\");\n")
    if xname=="d9":                 # EXX
        r[1],r[5] = r[5],r[1]
        r[2],r[6] = r[6],r[2]
        r[3],r[7] = r[7],r[3]
        ftest.write("   if (dut.reg_control_.bank_exx!==1) $fdisplay(f,\"* Bank EXX!=1\");\n")

    # Read the result: registers and memory
    # 0  1  2  3  4   5   6   7   8  9  10 11   (index)
    # AF BC DE HL AF' BC' DE' HL' IX IY SP PC
    RegRead("af", r[0])
    RegRead("bc", r[1])
    RegRead("de", r[2])
    RegRead("hl", r[3])
    RegRead("af2", r[4])
    RegRead("bc2", r[5])
    RegRead("de2", r[6])
    RegRead("hl2", r[7])
    RegRead("ix", r[8])
    RegRead("iy", r[9])
    RegRead("sp", r[10])
    #RegRead("pc", r[11]) Instead of PC, we read the address bus of the next instruction
    ftest.write("   if (pc!==16'h" + r[11] +  ") $fdisplay(f,\"* PC=%h !=" + r[11] +  "\",pc);\n")

    # 0 1 2    3    4  5        6          (index)
    # I R IFF1 IFF2 IM <halted> <tstates?>
    RegRead("ir", s[0]+s[1])

    # Read memory configuration until an empty line or -1 at the end
    while True:
        m = t2.pop(0).split(' ')
        m = list(filter(None, m))
        if len(m)==0 or m[0]=="-1":
            break
        address = int(m.pop(0),16)
        while True:
            d = m.pop(0)
            if d=="-1":
                break
            ftest.write("   if (ram.Mem[" + str(address) + "]!==8'h" + d + ") $fdisplay(f,\"* Mem[" + hex(address)[2:] + "]=%h !=" + d + "\",ram.Mem[" + str(address) + "]);\n")
            address = address+1
    # Read a list of IO checks that was compiled while parsing the initial condition
    while len(check_io)>0:
        ftest.write(check_io.pop(0))

# Write out the total number of clocks that this set of tests takes to execute
ftest.write("`define TOTAL_CLKS " + str(total_clks) + "\n")
ftest.write("$fdisplay(f,\"=== Tests completed ===\");\n")

# Touch a file that includes 'test_fuse.vh' to ensure it will recompile correctly
os.utime("test_fuse.sv", None)

// Copyright (C) 1991-2013 Altera Corporation
// Your use of Altera Corporation's design tools, logic functions 
// and other software and tools, and its AMPP partner logic 
// functions, and any output files from any of the foregoing 
// (including device programming or simulation files), and any 
// associated documentation or information are expressly subject 
// to the terms and conditions of the Altera Program License 
// Subscription Agreement, Altera MegaCore Function License 
// Agreement, or other applicable license agreement, including, 
// without limitation, that your use is for the sole purpose of 
// programming logic devices manufactured by Altera and sold by 
// Altera or its authorized distributors.  Please refer to the 
// applicable agreement for further details.

// PROGRAM		"Quartus II 64-Bit"
// VERSION		"Version 13.0.1 Build 232 06/12/2013 Service Pack 1 SJ Web Edition"
// CREATED		"Fri Feb 26 22:23:08 2016"

module ir(
	ctl_ir_we,
	clk,
	nreset,
	hold_clk_wait,
	db,
	opcode
);


input wire	ctl_ir_we;
input wire	clk;
input wire	nreset;
input wire	hold_clk_wait;
input wire	[7:0] db;
output reg	[7:0] opcode;

wire	SYNTHESIZED_WIRE_0;
wire	SYNTHESIZED_WIRE_1;




assign	SYNTHESIZED_WIRE_0 =  ~hold_clk_wait;

assign	SYNTHESIZED_WIRE_1 = ctl_ir_we & SYNTHESIZED_WIRE_0;


always@(posedge clk or negedge nreset)
begin
if (!nreset)
	begin
	opcode[7:0] <= 8'b00000000;
	end
else
if (SYNTHESIZED_WIRE_1)
	begin
	opcode[7:0] <= db[7:0];
	end
end


endmodule

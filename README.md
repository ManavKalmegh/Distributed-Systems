<!-- Example for lamport clock -->
local p1
local p2
send p1 p2 m1
send p1 p3 m2
send p3 p1 m3
receive p3 p1 m2
receive p1 p3 m3
receive p2 p1 m1
local p3

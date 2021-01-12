lda [:message]
ldb [:len]

loop:
sta :buffer1
lda 0xff
addab

jz :end

sta :buffer2
lda [:buffer1]

ldb 1
addab
outa

ldb [:buffer2]

jmp :loop

message:
.ascii "Hello World"
.const 0
len:
.const 11
buffer1:
.const 0
buffer2:
.const 0
end:
.const 0
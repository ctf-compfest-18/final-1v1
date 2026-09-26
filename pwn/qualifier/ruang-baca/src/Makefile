all:
	gcc -O0 -g0 -std=gnu11 -Wall -Wno-unused-result -Wno-stringop-overflow \
	    -fno-stack-protector -no-pie -fno-pie -static \
	    -o chall chall.c \
	    -static -no-pie -Wl,-z,noexecstack -lseccomp

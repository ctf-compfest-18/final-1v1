all:
	gcc -O0 -g0 -std=gnu11 -Wall -Wno-unused-result -Wno-stringop-overflow \
	    -fno-stack-protector -no-pie -fno-pie \
	    -o chall chall.c \
	    -no-pie -Wl,-z,noexecstack -Wl,-z,relro -Wl,-z,lazy
	sh strip-crt.sh ./chall
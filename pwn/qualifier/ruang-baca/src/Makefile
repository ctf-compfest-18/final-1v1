# Flags are pinned here on purpose. Changing any of them changes the challenge.
CC      := gcc
BIN     := chall

#  -O0                    keep the 0x40 buffer exactly where the source puts it
#  -fno-stack-protector   no canary
#  -no-pie -fno-pie       fixed addresses for gadgets, scratch and "/flag.txt"
#  -static                no libc leak needed, and no dynamic loader to abuse
#  -z noexecstack         NX on
CFLAGS  := -O0 -g0 -std=gnu11 -Wall -Wno-unused-result -Wno-stringop-overflow \
           -fno-stack-protector -no-pie -fno-pie -static
LDFLAGS := -static -no-pie -Wl,-z,noexecstack
LDLIBS  := -lseccomp

.PHONY: all clean
all: $(BIN)

$(BIN): chall.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

clean:
	rm -f $(BIN)

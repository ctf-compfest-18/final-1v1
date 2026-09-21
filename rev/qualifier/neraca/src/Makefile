# Flags are pinned here on purpose. Changing any of them changes the challenge.
CC      := gcc
BIN     := chall

#  -O0   keep the arithmetic legible; the read phase is the point
#  -s    stripped
#        dynamic link (gcc default), no -static
CFLAGS  := -O0 -g0 -std=gnu11 -Wall
LDFLAGS := -s

.PHONY: all clean
all: $(BIN)

$(BIN): chall.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(BIN)

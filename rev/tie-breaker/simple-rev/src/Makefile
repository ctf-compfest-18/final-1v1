CC      := gcc
CFLAGS  := -O0 -g0 -Wall -Wextra
TARGET  := chall

.PHONY: all clean

all: $(TARGET)

$(TARGET): chall.c
	$(CC) $(CFLAGS) -s -o $@ $<

clean:
	rm -f $(TARGET)
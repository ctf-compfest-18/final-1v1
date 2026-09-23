# Flags are pinned here on purpose. Changing any of them changes the challenge.
CC      := gcc
BIN     := chall

CFLAGS  := -O0 -g0 -std=gnu11 -Wall -Wno-unused-result -Wno-stringop-overflow \
           -fno-stack-protector -no-pie -fno-pie
LDFLAGS := -no-pie -Wl,-z,noexecstack -Wl,-z,relro -Wl,-z,lazy

.PHONY: all clean verify
all: $(BIN)

$(BIN): chall.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Produces the transcripts shipped with the challenge.
verify: $(BIN)
	checksec --file=./$(BIN) 2>&1 | tee checksec.txt
	@echo "--- strings ./$(BIN) | grep -i bin/sh   (must print nothing) ---" > strings.txt
	@if strings ./$(BIN) | grep -i "bin/sh" >> strings.txt; then \
	    echo "FAIL: /bin/sh present in binary"; exit 1; \
	 else echo "(no match - good)" >> strings.txt; fi
	@printf "\n--- strings ./$(BIN) ---\n" >> strings.txt
	@strings ./$(BIN) >> strings.txt
	@head -3 strings.txt
	@ROPgadget --binary ./$(BIN) > rop.all.tmp 2>&1
	@echo "--- gadgets touching rdi/rsi/rdx (none may be usable) ---" > ropgadget.txt
	@grep -E "(pop|mov|xchg) +(rdi|rsi|rdx|edi|esi|edx)" rop.all.tmp >> ropgadget.txt || echo "(none)" >> ropgadget.txt
	@printf "\n--- every pop gadget ---\n" >> ropgadget.txt
	@grep -E "^0x[0-9a-f]+ : pop " rop.all.tmp >> ropgadget.txt
	@printf "\n--- ROPgadget full listing ---\n" >> ropgadget.txt
	@cat rop.all.tmp >> ropgadget.txt; rm -f rop.all.tmp
	@echo VERIFY-OK

clean:
	rm -f $(BIN) checksec.txt strings.txt ropgadget.txt rop.all.tmp

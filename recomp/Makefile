# Static recompilation of K2: the demo (gen/: k2 as its own decruncher
# leaves it at &8000, ../tools/unpack.py, an AIF image on the Shared C
# Library) and the three modules it holds and inserts where they are
# (genmod1-3/: TimPlayer, ShonkFS, AutoVCache), from SuperSpider's analyse
# and gen, and game.c, linked with libroger (the RISC OS runtime).
ROGER   ?= $(HOME)/stuff/libroger
CC      ?= gcc
CFLAGS  ?= -O2 -g -w -fno-strict-aliasing $(if $(TRACE),-DRECOMP_TRACE)
# the modules: N:name:address - k2 has them copied into the RMA (OS_Module
# 11); these are their places there (game.c's modules)
MODS    := 1:timplayer:1800000 2:shonkfs:1830000 3:autovcache:1840000
GEN     := $(wildcard gen/code*.c) gen/entries.c
GENMOD  := $(foreach n,1 2 3,$(wildcard genmod$(n)/code*.c) genmod$(n)/entries.c)
OBJ     := $(GEN:.c=.o) $(GENMOD:.c=.o) game.o
LIBS    := $(shell pkg-config --libs sdl3) -lm -lpthread
INC     := -I$(ROGER)/include

k2: $(OBJ) $(ROGER)/libroger.a
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(ROGER)/libroger.a $(LIBS)

$(ROGER)/libroger.a: FORCE
	$(MAKE) -C $(ROGER) libroger.a

%.o: %.c $(ROGER)/include/roger.h $(ROGER)/include/roger_cpu.h
	$(CC) $(CFLAGS) $(INC) -c -o $@ $<

# Code/data analysis: SuperSpider, into ../analysis/<name>.json, then
# superspider gen. Each image's ../analysis/<name>.roots adds entry points
# to the analysis: "make roots" merges the gap entries a --trace-gaps run
# logged (untranslated.log, or LOG=...) into them, so the next "make regen"
# translates them.
SS      ?= $(HOME)/stuff/superspider
SSBIN   := $(SS)/_build/default/bin/main.exe
AN      := ../analysis
GAME    := ../unpacked/k2
LOG     ?= untranslated.log
# --no-smc: none of the images modifies its code

# --roots for ../analysis/<name>.roots, if there is one
roots = $(if $(wildcard $(AN)/$(1).roots),--roots $(AN)/$(1).roots)

regen:
	cd $(SS) && dune build
	python3 -I ../tools/unpack.py
	mkdir -p $(AN)
	$(SSBIN) analyse $(GAME) 8000 --full $(call roots,game) -o $(AN)/game.json
	for m in $(MODS); do n=$${m%%:*}; r=$${m#*:}; f=$${r%%:*}; a=$${r#*:}; \
	    $(SSBIN) analyse ../unpacked/$$f $$a --module --full \
	        $$([ -f $(AN)/$$f.roots ] && echo --roots $(AN)/$$f.roots) -o $(AN)/$$f.json || exit 1; done
	rm -rf gen genmod*
	$(SSBIN) gen $(GAME) 8000 $(AN)/game.json --c gen --leaders=dispatch --no-smc
	for m in $(MODS); do n=$${m%%:*}; r=$${m#*:}; f=$${r%%:*}; a=$${r#*:}; \
	    $(SSBIN) gen ../unpacked/$$f $$a $(AN)/$$f.json --c genmod$$n --leaders=dispatch --no-smc \
	        --prefix=M$$n --tabprefix=recompM$$n --files=1 --covtag=M$$n || exit 1; done

roots:
	python3 -I $(SS)/tools/gap_roots.py $(GAME) 8000 $(AN)/game.roots $(LOG)
	for m in $(MODS); do r=$${m#*:}; f=$${r%%:*}; a=$${r#*:}; \
	    python3 -I $(SS)/tools/gap_roots.py ../unpacked/$$f $$a $(AN)/$$f.roots $(LOG); done

clean:
	rm -f gen/*.o genmod*/*.o game.o k2

.PHONY: FORCE regen roots clean

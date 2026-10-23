K2 (DFI, 1998) - static recompilation
=====================================

A recipe: this repository holds no data from the demo. It rebuilds K2,
Paul Thomson's StrongARM Risc PC demo for DFI (1 December 1998; music by
Amberphene/TMWTP, played by Andre Timmermans' TimPlayer), as a native
executable from your own copy, recognised by content (recipe.json), so it
can be shared without distributing the demo.

    ./build.sh K2.zip
    cd recomp && ./k2

build.sh runs recipe.json's steps with SuperSpider's tools/weave.py
(~/stuff/superspider, or $SUPERSPIDER; $SS below): it extracts !k2,
runs the demo's own decruncher (tools/unpack.py, about a minute and a
half under $SS/tools/arm2.py), analyses and translates the demo and the
three modules it holds, and links them with libroger (~/stuff/libroger,
or make ROGER=...). Needs python3, OCaml/dune, gcc, SDL3 and, for
libroger, stb_image (Debian's libstb-dev).

The input, either of:

- K2 as Acorn User's CD 6 (December 1998) has it: EVOLA.EVOLUTION.K2/zip,
  copied off the CD - a Spark archive despite its name (995995 bytes,
  sha256 the recipe's known image);
- the later zip with K2Patch (January 1999: a module, for older
  machines, that claims the undefined instruction vector; not used here).

Only !k2 is used (its four files are the recipe's key files); the
ScreenMode files differ between the two and aren't needed.

What it makes:

    extracted/k2          !k2, via weave.py
    game/!k2              libroger's appdir (../game)
    unpacked/k2           tools/unpack.py: k2 as its decruncher leaves it, at
                          &8000 (an AIF image), and unpacked/timplayer,
                          shonkfs and autovcache, the modules in it
    analysis/*.json       SuperSpider's analyses (game and the modules);
    analysis/*.roots      committed: entry points found by --trace-gaps runs
    recomp/gen*/          their C translations
    recomp/k2             the demo

Committed: recipe.json, build.sh, tools/unpack.py, analysis/*.roots,
recomp/Makefile, recomp/game.c, recomp/k2.ini, this file.

Watching
--------

    ./k2                        the demo, start to end (about five and a half
                                minutes), then it exits
    ./k2 --crop                 as k2.ini says: all 384 rows

It draws as fast as the CPU allows (interactive runs are unthrottled) and
follows the music's position (TimPlayer's SongPosition) for its sequence.
Headless runs (--limit) count time at a StrongARM's 200 million
instructions a second (game.c's headless_mips): the whole demo is some 68
billion instructions (--limit=8e10).

How the demo is put together
----------------------------

!Run asks for 4400K of application memory and runs k2, packed with the
decruncher DFI's FishTank2 has: its first word branches to &FA6A8, which
decrunches the program to &8000-&3EA9AC (tools/unpack.py runs it). That
is an AIF image: C on the Shared C Library (which libroger provides) and
assembler, with zero-filled buffers in it (a megabyte from &4AEB8).

It checks that it can have 768K of screen memory and that the 512x384 mode
it uses is valid (in 8 and 15-bit colour: ScreenMode, the monitor
definition !Help asks you to merge, is 60Hz), and that the CPU is a
StrongARM (OS_PlatformFeatures 0, bit 0: code areas must be synchronised;
otherwise it offers to go on regardless). It has its three modules copied
into the RMA (OS_Module 11): TimPlayer 0.85 (the tracker player), ShonkFS
1.00 (DFI's: a filing system serving named blocks of memory as files,
which the program fills with its music, then has TimPlayer load
"ShonkFS::A.Music") and AutoVCache (StrongARM cache control: its
initialisation fails here - OS_MMUControl and OS_Memory 0 aren't there -
and the demo carries on without it). It claims EventV and the error
vector, starts the music and runs its parts (static, a chrome fish,
metaballs over fire, tubes and spheres in a tunnel, kaleidoscopes...),
setting the whole palette each frame (ColourTrans_WritePalette) and
fading through VIDC20's gamma tables (PaletteV 9).

Its assembler routines save SP in a literal word, use SP as a data
register and restore it from the word to return; several routines share
one word. The polygon clipper runs threaded code: a list of routine
addresses per outcode, from a table of 256, each ending ldr pc,[r12],#4.
TimPlayer has a jump table its guard (cmp r2,#16 ; movge r2,#0) lets
through with negative indices, into the table before it.

The translation: the demo (gen/, from &8000) and the modules (genmod1-3/,
translated for &1800000, &1830000 and &1840000, where libroger copies them:
game.c's modules, in_memory 2), all with --leaders=dispatch and --no-smc.
analysis/*.roots hold the clipper's routines and TimPlayer's negative-index
targets, from --trace-gaps runs (make roots); with them, a run from start
to end interprets nothing.

What it needed:

- SuperSpider: SP saved in a literal word shared by several routines -
  each restores its own (a restore site after its save and before the
  next save to the word continues its frame, not the others'); without it
  the analysis ran into the zero-filled buffers (289,000 "code" words, now
  8,300). OS_FSControl 12's filing system information block: its entries
  are code (src/riscos.ml). Also FishTank2's gen --no-smc. (The long
  multiplies added for these two demos turned out unused by either: K2's
  translated code has none, nor halfword transfers; what K2Patch does for
  older machines wasn't looked into.)
- libroger: OS_Module 11 (roger_module.in_memory 2: a module the program
  has copied into the RMA, translated for its place there, known by its
  title); filing systems that modules provide (src/modfs.c: OS_FSControl
  12/16, files read whole through FSEntry_Open/GetBytes/Close and served
  as host files); roger_config.strongarm (OS_PlatformFeatures 0);
  ColourTrans_WritePalette.

Not done: AutoVCache (OS_MMUControl, OS_Memory 0); the 60Hz vsync of the
demo's mode (libroger's vsync is always 50Hz).

/* K2 (DFI - Paul Thomson, 1 December 1998), a Risc PC demo for the
 * StrongARM: what libroger needs to know about it.
 *
 * !Run asks for 4400K of application memory and runs k2, an absolute packed
 * with the decruncher DFI's FishTank2 has (../tools/unpack.py runs it: the
 * image it leaves at &8000 is what's translated). That is an AIF image, C
 * on the Shared C Library (which libroger provides) and assembler, holding
 * three modules that it has copied into the RMA (OS_Module 11): TimPlayer
 * (Andre Timmermans' tracker player), ShonkFS (a filing system the music
 * is read through) and AutoVCache. It wants 768K of screen memory and a
 * 512x384 mode in both 8 and 15-bit colour (ScreenMode is the monitor
 * definition !Help asks you to merge: 60Hz), and a StrongARM
 * (OS_PlatformFeatures).
 *
 * The translated images: the demo (gen/) and the modules (genmod1-3/, at
 * the addresses libroger copies them to in the RMA). */
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <roger.h>

extern const struct roger_image recomp_image;                  /* gen/entries.c */
extern const struct roger_image recompM1_image, recompM2_image, recompM3_image;   /* genmod1-3 */

#define APP "../game/!k2"
static const char *const prefixes[] = {"<Obey$Dir>.", NULL};
/* the modules in k2, copied into the RMA (in_memory 2: known by title),
 * each translated for its place there (the Makefile's MODS) */
static const struct roger_module modules[] = {
    {"TimPlayer", &recompM1_image, 0, NULL, 2},
    {"ShonkFS", &recompM2_image, 0, NULL, 2},
    {"AutoVCache", &recompM3_image, 0, NULL, 2},
    {NULL, NULL, 0, NULL, 0}};

static struct roger_config config = {
    .title = "K2 (recompiled)",
    .image = &recomp_image,
    .image_path = "../unpacked/k2",
    .modules = modules,
    .appdir = "../game",
    .dir_prefixes = prefixes,
    .vidc20 = 1,                        /* a Risc PC: 8 and 16bpp modes, mode selectors */
    .strongarm = 1,                     /* which it checks for (OS_PlatformFeatures) */
    .initial_mode = 28,                 /* a desktop's: 640x480, 256 colours */
    .wimpslot = 4400 * 1024,            /* !Run: wimpslot -min 4400k */
    /* headless runs (--limit) at a StrongARM's speed, which it was written
     * for */
    .headless_mips = 200,
    /* code the analysis missed (none in a run from start to end, with the
     * roots files: the clipper's threaded code, run from a table of
     * routine lists, and TimPlayer's jump table entered with negative
     * indices) is interpreted rather than ending the run */
    .interpret_gaps = 1,
};

int main(int argc, char **argv) { roger_main(argc, argv, &config); }

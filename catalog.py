"""Generate ``docs/TOOLCHAINS.md`` — the toolchain catalog.

The catalog is derived from the two things that actually build the images:
``sources.json`` (what is pinned, what names resolve to what) and each
``<family>/<version>-<platform>/Dockerfile`` (how the compiler is run and
which wrapper the image exposes).  Nothing here is hand-maintained, so the
document cannot drift away from the images; ``make docs`` regenerates it and
``tests/test_catalog.py`` fails when the committed copy is stale.

Usage:
    python catalog.py            # rewrite docs/TOOLCHAINS.md
    python catalog.py --check     # exit 1 when the committed copy differs
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
DOC = REPO / "docs" / "TOOLCHAINS.md"
PROVENANCE = REPO / "docs" / "PROVENANCE.md"

#: ``<family>/<version>-<platform>`` suffixes, longest first so ``win16``
#: wins over a bare ``16``-style match and ``linux-x64`` over ``linux``.
PLATFORMS = (
    "linux-x64",
    "linux-i386",
    "dreamcast",
    "macos",
    "android-x86",
    "msdos",
    "switch",
    "win16",
    "win32",
    "x360",
    "wiiu",
    "psp",
    "nds",
    "3ds",
    "saturn",
    "ps1",
    "ps2",
    "n64",
    "gba",
    "wii",
    "gc",
)

#: Family → one-line description for the catalog heading.
FAMILIES = {
    "agbcc": "GBA decomp compilers (pret agbcc, the notyourav C++ fork, FE8J fork)",
    "agbccpp": "GBA decomp C++ compiler (notyourav/agbcc `cp` fork)",
    "armcc": "ARM Compiler for Nintendo 3DS",
    "borland": "Borland Turbo C/C++ (DOS and Win32)",
    "clang": "LLVM clang: native ELF hosts and the Switch decomp builds",
    "delphi": "Borland Delphi 1.0 (16-bit, DOSBox)",
    "ee-gcc": "Emotion Engine GCC for PlayStation 2",
    "gcc": "GNU/egcs and vendor GCC rebuilds (native and cross)",
    "ghs": "Green Hills C/C++ for Wii U",
    "icc": "Intel C++ Compiler for 32-bit Windows (i386 COFF)",
    "saturn": "Sega Saturn SH-2 toolchains (Cygnus 2.7-96Q3)",
    "ido": "SGI IDO MIPS compilers for N64 (recompiled and IRIX originals)",
    "iop-gcc": "I/O processor GCC for PlayStation 2",
    "mingw": "MinGW-w64 GCC cross compilers (i686 PE, wine)",
    "ndk": "Android NDK cross toolchains (i686-linux-android)",
    "msc": "Microsoft C 5.1 (16-bit DOS)",
    "msvc": "Microsoft Visual C/C++ 1.0-11.0",
    "msvc-ppc": "Microsoft Visual C++ for Xbox 360 (PowerPC)",
    "mwcc": "CodeWarrior PowerPC compilers (GameCube / Wii)",
    "mwccarm": "CodeWarrior ARM compilers (Nintendo DS ARM9)",
    "mwccpsp": "CodeWarrior compilers for PSP",
    "mwcps2": "CodeWarrior compilers for PlayStation 2",
    "prodg": "SN Systems ProDG compilers (GameCube)",
    "psp-gcc": "Sony PSP allegrex GCC (decompme/compilers 1.3.1)",
    "psyq": "Sony PSY-Q SDK toolchains (PS1)",
    "pspsnc": "Sony PSP System Narrow compiler",
    "shc": "Hitachi SuperH C compiler (Dreamcast)",
    "watcom": "Open Watcom C/C++ (32- and 16-bit)",
}

_ENTRYPOINT = re.compile(r'^ENTRYPOINT \["/usr/local/bin/([^"]+)"\]$', re.MULTILINE)

#: Every upstream a pinned download may come from, keyed by the part of the
#: URL that identifies it.  ``tests/test_catalog.py`` fails when a profile
#: pins a URL whose source is not listed here, so provenance — and the
#: licence class that goes with it — cannot be added silently.
SOURCES: dict[str, tuple[str, str]] = {
    "github.com/archaic-msvc": (
        (
            "our own preservation repos for the archived 32-bit Microsoft VC++ trees "
            "(`msvc1000` … `msvc900`, every service pack)"
        ),
        "proprietary",
    ),
    "github.com/archaic-toolchains": (
        (
            "our own preservation repos: reconstructed 16-bit MSVC / Turbo C / Delphi "
            "trees, the MSVC 4.0 and service-pack repos, and Borland C++ 5.5"
        ),
        "proprietary",
    ),
    "github.com/decompme": (
        (
            "decomp.me's compiler release assets (`decompme/compilers`: the vendor "
            "MWCCARM/ARMCC/MWCPS2/MWCCCPSP/SHC/PSY-Q/IRIX tools — proprietary — plus the "
            "Apache-2.0/GPL Android NDK repacks and psyq-obj-parser)"
        ),
        "proprietary",
    ),
    "files.decomp.dev": (
        (
            "dated decomp.me compiler bundles (the GameCube/Wii MWCC, ProDG and "
            "Xbox 360 MSVC trees; older dates stay addressable)"
        ),
        "proprietary",
    ),
    "github.com/decompals": (
        (
            "decompals rebuilds: `ido-static-recomp` (IDO for Linux), `old-gcc` "
            "(PS1/N64 GCC), `mips-gcc-2.7.2`, `mips-binutils-2.6`"
        ),
        "GPL (rebuilds of GPL toolchains)",
    ),
    "github.com/LLONSIT": (
        (
            "`qemu-irix-helpers`: the static qemu-irix user-mode emulator plus the "
            "original IRIX IDO / MIPSpro trees, commit-pinned"
        ),
        "mixed: GPL emulator, proprietary IRIX binaries",
    ),
    "github.com/bwrsandman": (
        (
            "`bwrsandman/icc5.0.1.010525Z`: the Intel C++ 5.0.1 (build 010525Z) "
            "tree, extracted from the archive.org item `latest-versions-of-c` "
            "(`data1.cab` md5 e8dd2defb4754dafe9295f2087a52be0).  A personal "
            "repository with one release, so the pin is sha256-verified and the "
            "same content also exists as git blobs (codeload fallback); mirror it "
            "before relying on it for a rebuild"
        ),
        "proprietary",
    ),
    "github.com/sozud": (
        (
            "`sozud/saturn-compilers`: the Sega Saturn Cygnus 2.7-96Q3 "
            "compiler and SDK media, commit-pinned"
        ),
        "proprietary",
    ),
    "github.com/mkst": (
        "`mkst/esa` `psyq-binaries`: the PSY-Q SDK releases (CCPSX/CC1PSX/ASPSX)",
        "proprietary",
    ),
    "ppa.launchpadcontent.net/dosemu2/ppa": (
        (
            "the `dosemu2/ppa` packages `dosemu2` (x86 virtualisation for DOS), "
            "`fdpp`/`libfdpp35`/`libfdldr35` (the FreeDOS++ kernel) and "
            "`comcom64`/`comcom32` — the DOS runtime the 16-bit toolchains run on"
        ),
        "GPL",
    ),
    "ppa.launchpadcontent.net/stsp-0/dj64": (
        (
            "the `stsp-0/dj64` PPA: the dj64 DPMI host (`dj64`, `djstub`, "
            "`libdjstub64-0`, `libdjdev64-0`) that lets DJGPP `go32` binaries "
            "run under dosemu2"
        ),
        "GPL",
    ),
    "FoxdieTeam": (
        (
            "`FoxdieTeam/psyq_sdk`: the PSY-Q 4.5 headers and libraries "
            "(commit-pinned tarball; the codeload archive hashes the same on "
            "repeat fetches, so the pin is sha256-verified like every other)"
        ),
        "proprietary",
    ),
    "github.com/pmret": (
        ("`gcc-papermario` / `binutils-papermario`: N64 rebuilds for the Paper Mario decomp"),
        "GPL",
    ),
    "github.com/Mr-Wiseguy": (
        "`Mr-Wiseguy/pcsx-redux` N64 release assets (cc1n64.exe, asn64.exe)",
        "GPL",
    ),
    "github.com/marijnvdwerf": (
        "`marijnvdwerf/sn64` release assets (the 2.8.1 cc1n64 / asn64)",
        "proprietary",
    ),
    "github.com/RocketRet": (
        "`RocketRet/modern-asn64`: the Python assembler driver used by the SNEW build",
        "MIT",
    ),
    "github.com/devwizard64": (
        "`devwizard64/gcc4.4.0-mips64-elf`: a prebuilt mips64-elf GCC 4.4.0 tree",
        "GPL",
    ),
    "github.com/ChrisNonyminus": (
        (
            "`ChrisNonyminus/powerpc-darwin-cross`: Apple cc1/cc1plus cross builds "
            "(powerpc-apple-darwin)"
        ),
        "GPL (Apple GCC sources)",
    ),
    "github.com/AngheloAlf": (
        "`AngheloAlf/egcs_1.1.2-4`: the N64 EGCS tree (mips-linux-gcc driver)",
        "GPL",
    ),
    "github.com/pret": ("`pret/agbcc`: the GBA compiler rebuild", "GPL"),
    "github.com/notyourav": ("`notyourav/agbcc`: the agbcc C++ frontend fork", "GPL"),
    "github.com/laqieer": ("`laqieer/agbcc`: the FE8J agbcc fork", "GPL"),
    "github.com/SBird1337": ("`SBird1337/camelot-gcc`: Camelot GCC 2.96 (GBA)", "GPL"),
    "github.com/niXman": ("`niXman/mingw-builds-binaries`: prebuilt MinGW-w64", "GPL"),
    "github.com/open-watcom": (
        "Open Watcom v2 release snapshots",
        "Sybase Open Watcom licence",
    ),
    "widberg": (
        ("`widberg/msvc8.0`: portable (patched) MSVC 8.0 repacks, commit-pinned per variant"),
        "proprietary",
    ),
    "earthsiege2": (
        (
            "`earthsiege2/borland-cpp-ide`: an archive of abandoned Borland C++ "
            "installations (the Borland C++ 5.6 command-line tree is extracted "
            "from it here)"
        ),
        "proprietary",
    ),
    "github.com/OmniBlade": (
        (
            "`OmniBlade/decomp.me` preservation releases: the DOS-era Watcom C/C++ "
            "10.5/10.5a/10.6/11.0 trees (and the `msvcwin9x` repacks)"
        ),
        "proprietary",
    ),
    "github.com/llvm": ("LLVM/Clang GitHub release assets", "Apache-2.0 with LLVM exception"),
    "releases.llvm.org": (
        (
            "LLVM's own release host, for the prebuilt clang tarballs that the "
            "3.9.1/4.0.1/8.0.0/9.0.0 GitHub releases do not carry"
        ),
        "Apache-2.0 with LLVM exception",
    ),
    "ftp.gnu.org": ("GNU GCC release tarballs, compiled inside the image", "GPL"),
    "deb.debian.org": (
        (
            "the Debian pool: the pinned `libtinfo5` runtime package the prebuilt "
            "clang trees link against (Debian dropped libtinfo5 from bookworm, so "
            "each clang image installs the .deb from the pool)"
        ),
        "MIT-style (ncurses); the .deb is taken unmodified",
    ),
    "gist.githubusercontent.com": (
        (
            "revision-pinned converter scripts: `Mc-muffin`'s `rof2elf.py` (SHC "
            "ROF → ELF) and `ChrisNonyminus`'s `convert_gas_syntax.py` (Apple cc1 "
            "assembler → GNU as)"
        ),
        "MIT (gists)",
    ),
}

#: Community (decomp.me) ids that resolve to images here, with the evidence.
#: Only rows whose equivalence was *verified* get an alias in ``sources.json``;
#: the rest explain why a same-version id is nevertheless a different build.
#: (decompme id, our profile, status, evidence)
EQUIVALENCES: tuple[tuple[str, str, str, str], ...] = (
    (
        "msvc6.3",
        "msvc-6.0-sp3",
        "verified alias",
        "`c1xx.dll` `28c355499c`, `c2.dll` `a0cc45f83f` — identical in both trees",
    ),
    (
        "msvc6.4",
        "msvc-6.0-sp4",
        "verified alias",
        "`c1xx.dll` `71718c2ba1`, `c2.dll` `5649bd68ed` — identical in both trees",
    ),
    (
        "msvc6.5",
        "msvc-6.0-sp5",
        "verified alias",
        "`c1xx.dll` `f014b3bee6`, `c2.dll` `d50100ac23` — identical in both trees",
    ),
    (
        "msvc6.5pp",
        "msvc-6.0-sp5-pp",
        "verified alias",
        "`c1xx.dll` `f014b3bee6`, `c2.dll` `6c8e3988a5` — identical in both trees",
    ),
    (
        "msvc6.6",
        "msvc-6.0-sp6",
        "verified alias",
        "`c1xx.dll` `ab4610ad56`, `c2.dll` `3f2b5f43e3` — identical in both trees",
    ),
    (
        "msvc6.0",
        "msvc-6.0-win9x",
        "verified alias (distinct build)",
        (
            "the win9x repack decomp.me serves under this id — shipped here as its own "
            "image because its front ends differ from `msvc-6.0`'s "
            "(`c1xx.dll` `71554a7688` vs `f3f0245453`), with the same banner 12.00.8168"
        ),
    ),
    (
        "bcc2.0",
        "borland-2.0-decompme",
        "verified alias (distinct build)",
        (
            "the decomp.me repack itself, shipped alongside `borland-2.0` (our "
            "`archaic-toolchains/tc20` media, different binaries)"
        ),
    ),
    (
        "bcc3.1",
        "borland-3.1-decompme",
        "verified alias (distinct build)",
        (
            "the decomp.me repack itself, shipped alongside `borland-3.1` (our "
            "`archaic-toolchains/tc31` media, different binaries)"
        ),
    ),
    (
        "msvc4.1",
        "msvc-4.1",
        "covered from our own repos",
        (
            "decomp.me's 4.1 asset and our `archaic-msvc/msvc410` tree carry the same "
            "`cl.exe` (`899f0f597f`), so the id needs no second image"
        ),
    ),
    (
        "msvc4.0",
        "msvc-4.0",
        "verified alias",
        (
            "decomp.me serves `itsmattkc/MSVC400@821e942f` for this id; our "
            "`archaic-toolchains/msvc400` tree has the same compilers "
            "(`cl.exe` `f097e736bb04`, `c1.exe` `7a7c14aff963`, `c1xx.exe` "
            "`3376b1dfaff0`)"
        ),
    ),
    (
        "msvc4.2",
        "msvc-4.2",
        "verified alias",
        (
            "decomp.me serves `itsmattkc/MSVC420@df2c13aa`; byte-identical to our "
            "`archaic-msvc/msvc420` (`cl.exe` `c5bf7ad84482`, `c1.exe` `c5a62937d806`, "
            "`c1xx.exe` `9e0782ec157b`)"
        ),
    ),
    (
        "msvc7.1",
        "msvc-7.1",
        "verified alias",
        (
            "decomp.me serves OmniBlade's win9x repack (`msvc7.0.tar.gz`) under this "
            "id; our `archaic-msvc/msvc710` `Vc7/bin` carries the same compiler "
            "(`cl.exe` `2ecf86a3edfd`, `c1.dll` `11f452af93f8`, `c1xx.dll` "
            "`353f3d5dcd05`, `c2.dll` `bcd28f39b179`) — only stray `.config`/`.sql` "
            "files differ"
        ),
    ),
    (
        "msvc7.0",
        "msvc-7.0",
        "covered from our own repos",
        (
            "we ship the RTM tree as `msvc-7.0` (`archaic-msvc/msvc700`, "
            "13.00.9466) and SP1 as `msvc-7.0-sp1`; the old `msvc-7.0-rtm` profile "
            "pinned the same tarball byte-for-byte, so it is now an alias rather "
            "than a second image.  Note: this profile used to point at the *7.1* "
            "tree (13.10.3077) — the same compiler as `msvc-7.1`"
        ),
    ),
    (
        "msvc8.0p",
        "msvc-8.0-portable",
        "verified alias (distinct build)",
        (
            "the portable repack decomp.me serves for this id: same banner "
            "(14.00.50727.42) as `msvc-8.0` but patched binaries "
            "(`cl.exe` `6e7de73a82ac` vs `3cbf4306526c`).  The repack's other commit "
            "(`msvc8.0`, d6c4aa20) *is* byte-identical to ours and is not shipped twice"
        ),
    ),
    (
        "ido5.3_c++_irix",
        "ido-5.3-cxx",
        "verified alias",
        (
            "decomp.me declares this as `base_compiler=IDO53_CXX`, so it is the same "
            "`ido5.3_c++.tar.xz` tree behind the same `usr/lib/CC` driver under "
            "qemu-irix — only the platform label differs from `ido5.3_c++`"
        ),
    ),
    (
        "ido6.0_irix",
        "ido-6.0",
        "verified alias",
        ("`base_compiler=IDO60`: same `ido6.0.tar.xz` tree, same `usr/lib/driver` under qemu-irix"),
    ),
    (
        "ido7.1_irix",
        "ido-7.1",
        "verified alias",
        (
            "`base_compiler=IDO71`: the same `ido-7.1-recomp-linux.tar.gz` recomp tree "
            "and the same `cc` driver"
        ),
    ),
    (
        "ido7.1_c++",
        "ido-7.1-cxx",
        "verified alias",
        (
            "the same `ido-7.1-recomp-linux.tar.gz` tree, entered through `NCC` "
            "(drags in `acpp` + `edgcpfe`); it is a separate image because the `cc` "
            "entrypoint of `ido-7.1` rejects C++ sources outright"
        ),
    ),
    (
        "mips_pro_744_irix",
        "ido-mipspro-744",
        "verified alias",
        (
            "`base_compiler=MIPS_PRO_744`: same `mipspro7.4.4.tar.xz` tree, same "
            "`usr/lib/driver` under qemu-irix"
        ),
    ),
    (
        "ido5.3_asm_irix",
        "ido-5.3-irix",
        "verified alias",
        (
            "IDO 5.3 with the assembler dialect selected (`.s` input); the driver is "
            "the same `cc`, the id only switches decomp.me's language flag"
        ),
    ),
    (
        "ido5.3_irix",
        "ido-5.3-irix",
        "equivalent (different artifact)",
        (
            "decomp.me runs its *static recompilation* of 5.3 on the IRIX platform "
            "here; we ship the genuine IRIX `cc` from `ssb_ido5.3.tar` instead "
            "(`cc` `e197752a2c21`, byte-identical to the `ido_root.tar.xz` tree), so "
            "the compiler is the same one with better provenance"
        ),
    ),
    (
        "ssb_ido5.3",
        "ido-5.3-irix",
        "equivalent (same tree)",
        (
            "the smash-brothers decomp id names the `ssb_ido5.3.tar` asset we pin; the "
            "`usr/irix4` sub-tree of that archive is the part that does not run here"
        ),
    ),
    (
        "gcc2.7.2sn0001-cxx",
        "gcc-2.7.2-sn0001-cxx",
        "verified alias",
        (
            "same `n64_sn272_0001.tar.gz` tree as `gcc2.7.2sn0001` with the C++ cpp "
            "defines and `cc1pln64.exe`; the C image's pipeline feeds `cpp -lang-c` "
            "into `cc1n64.exe`, which yields an empty object for C++ input"
        ),
    ),
    (
        "gcc2.7.2sn0006-cxx",
        "gcc-2.7.2-sn0006-cxx",
        "verified alias",
        (
            "same `n64_sn272_0006.tar.gz` tree as `gcc2.7.2sn0006`, C++ front end and "
            "defines — the C image cannot serve C++ at all"
        ),
    ),
    (
        "gcc2.8.1sn-cxx",
        "gcc-2.8.1-sn-cxx",
        "verified alias",
        (
            "the `marijnvdwerf/sn64` 2.8.1 assets as `gcc2.8.1sn` plus the "
            "`cc1pln64.exe` front end that the C profile does not install"
        ),
    ),
    (
        "gcc2.8.1snew-cxx",
        "gcc-2.8.1-snew-cxx",
        "verified alias",
        (
            "the same 2.8.1 front ends with `modern-asn64.py` as the assembler; "
            "decomp.me's `gcc2.8.1snew-cxx` reuses the 2.8.1 asset rather than our "
            "`gcc2.7.2snew` tree"
        ),
    ),
    (
        "gcc-5026-cpp",
        "gcc-4.0.0-5026",
        "verified alias (same image)",
        (
            "the C image already selects `cc1plus` for `.cpp`/`.cc`/`.C` sources — "
            "its wrapper carries exactly decomp.me's `GCC_CC1PLUS_ALT` pipeline, and "
            "C++ compiles to a PowerPC object in both"
        ),
    ),
    (
        "gcc-5363-cpp",
        "gcc-4.0.1-5363",
        "verified alias (same image)",
        "same tree and same `cc1plus` route as the C image, as for `gcc-5026-cpp`",
    ),
    (
        "gcc-5370-cpp",
        "gcc-4.0.1-5370",
        "verified alias (same image)",
        (
            "this tree keeps `cc1plus` under `powerpc-darwin-cross/bin/`, which is "
            "where the C image's wrapper looks — exactly decomp.me's `GCC_CC1PLUS`"
        ),
    ),
    (
        "wpp10.0a",
        "watcom-10.0a-cxx",
        "verified alias",
        (
            "the same `wcc10.0a.tar.gz` media as `wcc10.0a` entered through "
            "`binnt/wpp386.exe`; decomp.me's `WATCOM_CXX` differs from `WATCOM_CC` in "
            "that one binary, which an alias cannot express"
        ),
    ),
    (
        "wpp10.5",
        "watcom-10.5-cxx",
        "verified alias",
        "the `wcc10.5.tar.gz` media, C++ driver (`wpp386.exe`) instead of `wcc386.exe`",
    ),
    (
        "wpp10.5a",
        "watcom-10.5a-cxx",
        "verified alias",
        "the `wcc10.5a.tar.gz` media, C++ driver (`wpp386.exe`) instead of `wcc386.exe`",
    ),
    (
        "wpp10.6",
        "watcom-10.6-cxx",
        "verified alias",
        "the `wcc10.6.tar.gz` media, C++ driver (`wpp386.exe`) instead of `wcc386.exe`",
    ),
    (
        "wpp11.0",
        "watcom-11.0-cxx",
        "verified alias",
        "the `wcc11.0.tar.gz` media, C++ driver (`wpp386.exe`) instead of `wcc386.exe`",
    ),
    (
        "old_agbcc",
        "agbcc-old-gba",
        "verified alias",
        (
            "the `pret/agbcc` release asset as `agbcc`, entered through the tree's "
            "`bin/old_agbcc`; decomp.me declares it `base_compiler=AGBCC`"
        ),
    ),
    (
        "agbcc_arm",
        "agbcc-arm-gba",
        "verified alias",
        (
            "the same asset entered through `bin/agbcc_arm`, which emits ARM-mode code "
            "where `agbcc` emits Thumb (`for ARM/elf` vs `for Thumb/elf` in its banner), "
            "also `base_compiler=AGBCC` upstream"
        ),
    ),
    (
        "psyq3.3",
        "psyq-3.3",
        "verified alias",
        (
            "the `mkst/esa` psyq3.3 asset driven by decomp.me's PSYQ_MSDOS_CC recipe; "
            "that recipe needs DOSEMU, which Debian dropped, so this image runs the "
            "same CC1PSX/ASPSX stages under dosemu2 + dj64 (see base-dosemu)"
        ),
    ),
    (
        "psyq3.5",
        "psyq-3.5",
        "verified alias",
        "the `mkst/esa` psyq3.5 asset, same DOS pipeline as `psyq3.3`",
    ),
    (
        "psyq3.6",
        "psyq-3.6",
        "verified alias",
        "the `mkst/esa` psyq3.6 asset, same DOS pipeline as `psyq3.3`",
    ),
    (
        "psyq_263_221",
        "psyq-2.6.3-221",
        "verified alias",
        (
            "decomp.me's own repack of PSY-Q 2.6.3 (CC1PSX + ASPSX + the parser) under "
            "the dosemu2 pipeline; the asset already carries psyq-obj-parser"
        ),
    ),
    (
        "cygnus-2.7-96Q3",
        "saturn-cygnus-2.7-96Q3",
        "verified alias",
        (
            "the `sozud/saturn-compilers` `cygnus-2.7-96Q3-bin` subtree (CPP/CC1/AS) "
            "under dosemu2; the final coff-sh -> elf32-sh conversion uses "
            "`sh-elf-objcopy` as in decomp.me's recipe, because the archive's own DOS "
            "OBJCOPY.EXE exits 1 under the emulator"
        ),
    ),
    (
        "icc5.0.1-010525z",
        "icc-5.0.1-010525z",
        "verified alias",
        (
            "decomp.me's two-file recipe for this id is Microsoft C 6.0 (linker) plus "
            "`bwrsandman/icc5.0.1.010525Z`; an earlier round here downloaded only the "
            "first file and mis-filed the id as *not an Intel compiler*.  Compiling "
            "(`/c`) needs just the Intel tree, whose `icl.exe` reports Version 5.0.1 "
            "Build 010525Z"
        ),
    ),
    (
        "ido4.1",
        "ido-4.1",
        "verified alias",
        (
            "decomp.me's `ido4.1` recipe (bundled `qemu-irix-4.0` running the IRIX "
            "`cc` with `-EL`, then the asset's own `ecoff_tool.py`).  It was blocked "
            "here until the image moved to a GLIBC_2.38+ base: Ubuntu noble's 2.39 "
            "loads that emulator where bookworm's 2.36 aborted"
        ),
    ),
    (
        "psp-gcc-1.3.1",
        "psp-gcc-1.3.1",
        "covered by the profile key",
        (
            "the asset's split layout (driver in `psp/bin`, internals in `lib/gcc-lib`) "
            "reassembled under the prefix the driver hard-codes, `/usr/local/psp/devkit`. "
            "An earlier round recorded it as blocked because `as`/`ld` looked empty — "
            "they are real 32-bit i386 binaries; what is missing is the "
            "`pspspecs`/`pspfixup`/`psplibgen` trio that only matters for linking"
        ),
    ),
)

#: Ids catalogued upstream but deliberately not shipped here, with the concrete
#: reason: either a provenance problem (an asset that cannot produce a working
#: image) or a catalogued entry that is not a compiler at all.  Neither is
#: simply missing work.
GAPS: tuple[tuple[str, str], ...] = (
    (
        "IDO IRIX4-flavoured trees (`ido7.1_irix4`, `ido7.1_irix4_c++`)",
        (
            "these are not vendor toolchains but decomp.me's own `cc-irix4` driver "
            "stitching three trees together (the 4.1 front end, the 5.3 `c++` cfront "
            "and the 7.1 backend, the latter two from archives we do pin).  The "
            "GLIBC_2.38 obstacle is gone — `ido/4.1-n64` runs the bundled "
            "`qemu-irix-4.0` on the Ubuntu-noble base — so what remains is that no "
            "vendor id maps to this franken-driver; the plain `ido7.1_irix` id *is* "
            "shipped as the static recomp"
        ),
    ),
    (
        "IDO Pascal ids (`ido5.3Pascal`, `ido7.1Pascal`)",
        (
            "decomp.me reuses the C recomp assets and only flips a language flag; "
            "neither `ido-5.3-recomp-linux.tar.gz` nor `ido-7.1-recomp-linux.tar.gz` "
            "contains a Pascal front end (`pc`), so there is no artifact to ship"
        ),
    ),
    (
        "`wibo_dlls`",
        (
            "not a compiler: decomp.me's dated `msvcrt_*.zip` DLL bundle that its "
            "wibo-backed Windows toolchains mount at run time.  Our images get the "
            "same effect from the shared base image's wine/wibo prefix"
        ),
    ),
    (
        "`dummy_longrunning`",
        "not a compiler: decomp.me's job-timeout fixture (`sleep 3600`)",
    ),
    (
        "psp-gcc 1.7.1 (`psp-gcc-1.7.1`)",
        (
            "its asset ships **0-byte** `psp/bin/as` and `psp/bin/ld` (verified), so "
            "the driver's cc1 runs and then fails with \"cannot exec "
            '`/usr/local/psp/devkit/bin/as`: Exec format error".  `psp-gcc-1.3.1` '
            "from the same release series carries real 32-bit binutils and *is* "
            "shipped; note that decomp.me's own compiler list serves only 1.3.1 "
            "as well"
        ),
    ),
)


#: Manifest keys that may hold a pinned download URL.
URL_KEYS = ("url", "binutils_url", "parser_url", "helper_url", "sdk_url")


def urls_of(entry: dict[str, object]) -> list[str]:
    """Every download URL a profile pins, primary and secondary alike."""
    found = [u for key in URL_KEYS if (u := _text(entry, key))]
    extra = entry.get("extra_pins", [])
    if isinstance(extra, list):
        for pin in extra:
            if isinstance(pin, dict):
                found.extend(u for key in ("url",) if (u := _text(pin, key)))
    return found


def source_of(url: str) -> str:
    """The ``SOURCES`` key a pinned URL belongs to (``""`` when unknown).

    The *longest* matching key wins, not the first in insertion order: keys are
    host prefixes, so a more specific one (``host/org/repo``) must beat the
    generic host (``host``) regardless of how the table is written.
    """
    return max((key for key in SOURCES if key in url), key=len, default="")


def manifest() -> dict[str, dict[str, object]]:
    """The parsed ``sources.json`` keyed by profile name."""
    text = (REPO / "sources.json").read_text(encoding="utf-8")
    data: dict[str, dict[str, object]] = json.loads(text)
    return data


def _text(entry: dict[str, object], key: str) -> str:
    value = entry.get(key, "")
    return value if isinstance(value, str) else ""


def _aliases(entry: dict[str, object]) -> list[str]:
    value = entry.get("aliases", [])
    return [str(a) for a in value] if isinstance(value, list) else []


def _platform(host_dir: str) -> str:
    version_arch = host_dir.split("/", 1)[1] if "/" in host_dir else host_dir
    return next((p for p in PLATFORMS if version_arch.endswith(p)), "host")


def _image_sources(host_dir: str) -> str:
    """A Dockerfile plus its sibling wrapper files, as one blob.

    Wrappers live either inline (``printf`` into ``/usr/local/bin``) or in a
    ``*.sh`` next to the Dockerfile.  Reading only the Dockerfile made the
    runtime column read ``?`` for every image that shipped an external wrapper
    — 32 rows of the catalog — and hid their notes.
    """
    d = REPO / host_dir
    parts = [(d / "Dockerfile").read_text(encoding="utf-8")]
    parts += [p.read_text(encoding="utf-8") for p in sorted(d.glob("*.sh"))]
    return "\n".join(parts)


#: How each recipe's runner is described in the catalog.  This used to be
#: sniffed out of the rendered Dockerfile, which read `?` for every image with
#: an external wrapper and quietly disagreed with the manifest; the recipe
#: carries the answer, and a contract test keeps the two in step.
_RUNTIME = {
    "exec": "native",
    "wine": "wine, wibo via `REBREW_RUNNER=wibo`",
    "wibo": "wibo (default), wine via `REBREW_RUNNER=wine`",
    "dosbox": "DOSBox",
    "dosemu2": "dosemu2 (needs `--device /dev/kvm`)",
}


def _runtime(entry: dict[str, object]) -> str:
    """How the image executes its compiler, from the recipe it declares."""
    recipe = entry.get("recipe")
    runner = _text(recipe, "runner") if isinstance(recipe, dict) else ""
    return _RUNTIME.get(runner, "?")


#: Install plumbing that mentions a helper's name without running it: the
#: download/checksum/chmod lines and the tarball steps around them.
_PLUMBING = (
    "curl ",
    "tar ",
    "chmod ",
    "sha256sum",
    "mkdir -p",
    "rm -rf",
    "rm /tmp",
    "ls /opt",
    "apt-get",
    "COPY ",
)


def _wrapper_text(blob: str) -> str:
    """The blob minus comments and install plumbing — i.e. what actually runs.

    A substring search over the whole Dockerfile cannot tell `rof2elf.py` being
    *downloaded* from being *invoked* (and `chmod +x .../rof2elf.py ...` is on
    the same line as the tool's name).  Only a command that reaches the tool
    with arguments counts here.
    """
    keep = []
    for line in blob.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or any(tok in line for tok in _PLUMBING):
            continue
        keep.append(line)
    return "\n".join(keep)


def _runs(blob: str, tool: str) -> bool:
    """True when the wrapper executes ``tool`` with an argument."""
    return re.search(rf"{re.escape(tool)}[ \t]+(?![\\\n])", _wrapper_text(blob)) is not None


def _notes(profile: str, entry: dict[str, object], dockerfile: str) -> str:
    """Per-image caveats a consumer has to know before invoking it."""
    notes: list[str] = []
    base = _text(entry, "variant_of")
    if base:
        notes.append(f"the same build as `{base}`, with a different front end")
    layout = _text(entry, "layout")
    if layout not in ("tar", "tar-strip1", ""):
        notes.append(f"unpacked from `{layout}`")
    if "rof2elf.py" in dockerfile:
        notes.append(
            "converts its ROF `.obj` with the image's `rof2elf.py`"
            if _runs(dockerfile, "rof2elf.py")
            else "emits a ROF `.obj`; convert with the image's `rof2elf.py`"
        )
    if "psyq-obj-parser" in dockerfile:
        notes.append(
            "converts its Sony object with the image's `psyq-obj-parser`"
            if _runs(dockerfile, "psyq-obj-parser")
            else "emits a Sony object; convert with the image's `psyq-obj-parser`"
        )
    if "usr/lib/CC" in dockerfile:
        notes.append(
            "entered through the vendor C++ driver (`usr/lib/CC`): `.C`/`.cc` only, "
            "`.cpp` is silently ignored"
        )
    if "/7.1/NCC" in dockerfile:
        notes.append("entered through the vendor C++ driver (`NCC`)")
    if profile.startswith(("agbcc", "agbccpp")):
        notes.append("cc1-style: emits assembly, not an object")
    if _text(entry, "binutils_url"):
        notes.append("pins a second source (binutils)")
    if _text(entry, "parser_url"):
        notes.append("pins a second source (obj parser)")
    if _text(entry, "helper_url"):
        notes.append("pins a second source (converter script)")
    if _text(entry, "sdk_url"):
        notes.append("pins a second source (SDK headers/libs)")
    if "release" in _text(entry, "url") and profile.startswith("agbcc"):
        notes.append("upstream release tag is rebuilt on every push — re-pin on drift")
    if "rebrew_dosemu_run" in dockerfile:
        notes.append(
            "1994 DJGPP `go32` DOS binaries run under dosemu2 — DOSBox cannot load "
            "their stub — so the container needs `--device /dev/kvm`"
        )
    if "convert_gas_syntax.py" in dockerfile:
        notes.append(
            "Apple cc1 output goes through decomp.me's `convert_gas_syntax.py`, which "
            "emits only the translation unit's first function"
        )
    if "cc1pln64.exe" in dockerfile:
        notes.append("C++ id: `cpp -lang-c++` into the C++ front end `cc1pln64.exe`")
    return "; ".join(notes) or "—"


def _pin(entry: dict[str, object]) -> str:
    url = _text(entry, "url")
    sha = _text(entry, "sha256")
    commit = _text(entry, "commit")
    name = url.split("?")[0].rstrip("/").split("/")[-1] or url
    pin = f"`{name}` `{sha[:12]}`"
    return f"{pin} @ `{commit[:12]}`" if commit else pin


def render(entries: dict[str, dict[str, object]]) -> str:
    """The full markdown catalog for the given manifest."""
    rows: dict[str, list[tuple[str, dict[str, object]]]] = {}
    for profile, entry in entries.items():
        family = _text(entry, "family") or profile.split("-")[0]
        rows.setdefault(family, []).append((profile, entry))

    out: list[str] = [
        "<!-- Generated by catalog.py — do not edit by hand. -->",
        "<!-- Regenerate with `make docs`. -->",
        "",
        "# Toolchain catalog",
        "",
        f"{len(entries)} toolchains, one self-contained image each.  This file is generated",
        "from `sources.json` and the toolchain Dockerfiles; see",
        "[ADDING-TOOLCHAIN.md](ADDING-TOOLCHAIN.md) to add another, and the",
        "[README](../README.md) for how to run the images.",
        "",
        "Every tag is `rebrew/<family>:<version>-<platform>` (`PREFIX=` re-tags the",
        "whole set).  The runtime column says how the image executes its compiler;",
        "the notes column flags the toolchains whose output needs a second step.",
        "",
        "## At a glance",
        "",
        "| Platform | Toolchains |",
        "| --- | --- |",
    ]
    by_platform: dict[str, int] = {}
    for _profile, entry in entries.items():
        platform = _platform(_text(entry, "host_dir"))
        by_platform[platform] = by_platform.get(platform, 0) + 1
    for platform, count in sorted(by_platform.items()):
        out.append(f"| {platform} | {count} |")

    for family in sorted(rows):
        out += [
            "",
            f"## {family}",
            "",
            FAMILIES.get(family, ""),
            "",
            "| Image tag | Platform | Entrypoint | Runtime | Aliases | Pinned source | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        family_rows: list[tuple[str, dict[str, object]]] = rows[family]
        for _profile, entry in sorted(family_rows, key=lambda item: _text(item[1], "host_dir")):
            host_dir = _text(entry, "host_dir")
            version_arch = host_dir.split("/", 1)[1] if "/" in host_dir else host_dir
            dockerfile = (REPO / host_dir / "Dockerfile").read_text(encoding="utf-8")
            match = _ENTRYPOINT.search(dockerfile)
            entrypoint = f"`{match.group(1)}`" if match else "—"
            aliases = ", ".join(f"`{a}`" for a in _aliases(entry)) or "—"
            blob = _image_sources(host_dir)
            out.append(
                f"| `rebrew/{family}:{version_arch}` | {_platform(host_dir)} | {entrypoint} "
                f"| {_runtime(entry)} | {aliases} | {_pin(entry)} "
                f"| {_notes(_profile, entry, blob)} |"
            )
    out.append("")
    return "\n".join(out)


def provenance(entries: dict[str, dict[str, object]]) -> str:
    """Render ``docs/PROVENANCE.md`` — where every pinned download comes from."""
    per_source: dict[str, list[str]] = {}
    for profile, entry in entries.items():
        for url in urls_of(entry):
            per_source.setdefault(source_of(url), []).append(profile)

    out: list[str] = [
        "<!-- Generated by catalog.py — do not edit by hand. -->",
        "<!-- Regenerate with `make docs`. -->",
        "",
        "# Provenance",
        "",
        "Every image here is built from a sha256-pinned download; no compiler",
        "binary is redistributed from this repository. The chain is:",
        "",
        "1. the original vendor media (CDs, floppies, SDK releases) is preserved",
        "   in archival repos;",
        "2. those trees are packaged as release assets or dated bundles, and",
        "   `sources.json` pins each one by `url` + `sha256` (plus the git",
        "   `commit` for branch-pinned tarballs);",
        "3. the Dockerfile re-verifies that hash during the build, so an image",
        "   either matches this manifest or fails to build.",
        "",
        "Three kinds of upstream are involved: **our own preservation repos**",
        "(`archaic-msvc` / `archaic-toolchains`), **community rebuild repos**",
        "(`decompals`, `decompme/compilers`, `pret/agbcc`, …), and **vendor",
        "hosts** (`releases.llvm.org`, `ftp.gnu.org`).  The table below is",
        "generated from the manifest; `make test` fails if a pinned URL is not",
        "listed here, so a new upstream cannot arrive undocumented.",
        "",
        "| Upstream | What it hosts | Licence class | Toolchains |",
        "| --- | --- | --- | --- |",
    ]
    for key in sorted(per_source, key=lambda k: (-len(per_source[k]), k)):
        label, licence = SOURCES.get(key, ("**UNDOCUMENTED — add to `SOURCES`**", "unknown"))
        profiles = sorted(set(per_source[key]))
        out.append(f"| `{key or '?'}` | {label} | {licence} | {len(profiles)} |")

    # Upstreams that no *profile* pins belong to the shared bases, whose pins
    # live in base-basename*/Dockerfile rather than in sources.json.  They are
    # real runtime dependencies of whole families (the DOS images run on
    # dosemu2 + dj64), so they are rendered here instead of sitting in SOURCES
    # as unreachable data.
    shared = [key for key in sorted(SOURCES) if key not in per_source]
    if shared:
        out += [
            "",
            "## Shared bases",
            "",
            "These upstreams are not pinned by any profile — they are what the",
            "shared base images install, and each base Dockerfile carries the",
            "sha256-pinned package list:",
            "",
        ]
        for key in shared:
            label, licence = SOURCES[key]
            out.append(f"- `{key}` — {label} ({licence})")

    out += [
        "",
        "## Community id mappings",
        "",
        "decomp.me names some of these compilers differently.  Where the images",
        "are provably the same compiler, the community id is registered as an",
        "alias (`./build.sh msvc6.5` builds `msvc/6.0-sp5-win32`); where only the",
        "version matches, the row says so rather than pretending to be a match.",
        "",
        "| Community id | Image here | Status | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for community, profile, status, evidence in EQUIVALENCES:
        entry = entries.get(profile, {})
        host_dir = _text(entry, "host_dir") if isinstance(entry, dict) else ""
        target = f"`{host_dir}`" if host_dir else profile
        out.append(f"| `{community}` | {target} | {status} | {evidence} |")

    out += [
        "",
        "## Licensing",
        "",
        "- The **build glue** in this repository (Dockerfiles, wrappers, the base",
        "  image, `sources.json`, the generators) is MIT.",
        "- The **GCC-derived console compilers** (IDO recompilations, `old-gcc`,",
        "  `agbcc` and its forks, Camelot GCC, the papermario rebuilds, MinGW-w64,",
        "  and the in-image GNU GCC builds) are GPL, fetched from their rebuild",
        "  repos at build time.",
        "- The **vendor compilers** (Microsoft, Borland, Watcom, Sony, Nintendo,",
        "  Sega, SN Systems, Silicon Graphics, Intel) are proprietary and are",
        "  fetched from the preservation repos named above; obtaining or using",
        "  them is at your own discretion.",
        "- The **IRIX IDO/MIPSpro images** combine a GPL emulator (`qemu-irix`,",
        "  vendored in the same bundle) with proprietary IRIX binaries.",
        "",
        "Per-profile pins — URL, sha256, commit, archive layout — are in the",
        "[toolchain catalog](TOOLCHAINS.md) and in [`sources.json`](../sources.json).",
        "",
        "## Catalogued but not shipped",
        "",
        "These upstream entries exist but do not currently produce a working",
        "image here.  Each is a provenance/asset problem, not an oversight:",
        "",
        "| Toolchain | Why it is not shipped |",
        "| --- | --- |",
    ]
    for name, reason in GAPS:
        out.append(f"| {name} | {reason} |")
    out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    """Write the catalog, or (``--check``) verify the committed copy."""
    entries = manifest()
    rendered = render(entries)
    rendered_provenance = provenance(entries)
    if "--check" in argv:
        stale = []
        for path, expected in ((DOC, rendered), (PROVENANCE, rendered_provenance)):
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != expected:
                stale.append(str(path.relative_to(REPO)))
        if stale:
            print(f"stale: {', '.join(stale)} — run `make docs`", file=sys.stderr)
            return 1
        print("docs are up to date")
        return 0
    for path, text in ((DOC, rendered), (PROVENANCE, rendered_provenance)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

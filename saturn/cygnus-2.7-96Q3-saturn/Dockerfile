# Saturn Cygnus 2.7-96Q3 — Sega Saturn SH-2 SDK compiler, DOS binaries under dosemu2.
#
# Inherits rebrew/base-dosemu because CPP.EXE / CC1.EXE / AS.EXE are DOS
# binaries (the tree ships GO32.EXE and EMU387 for the same reason) that
# DOSBox cannot load.  decomp.me's recipe, with every stage in its own
# dosemu2 session:
#
#   CPP.EXE src.c -o src_proc.c
#   CC1.EXE -quiet <flags> src_proc.c -o output.s
#   AS.EXE output.s -o output.o
#   sh-elf-objcopy -Icoff-sh -Oelf32-sh output.o out.o
#
# The conversion is decomp.me's: the archive's own DOS OBJCOPY.EXE runs under
# dosemu2 but exits 1 with no output for this conversion (verified), so the
# Linux `sh-elf-objcopy` from Ubuntu's binutils-sh-elf does it instead.
#
# NOTE: this image needs `--device /dev/kvm` at run time; the wrapper explains
#       that if the device is missing.
#
# Build:  docker build -t rebrew/saturn:cygnus-2.7-96Q3-saturn saturn/cygnus-2.7-96Q3-saturn
# Invoke: docker run --rm --device /dev/kvm -v "$PWD":/work -w /work rebrew/saturn:cygnus-2.7-96Q3-saturn -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Saturn Cygnus 2.7-96Q3 (dosemu2)" \
      org.opencontainers.image.description="Cygnus 2.7-96Q3 (SH-2, Sega Saturn, DOS binaries under dosemu2) toolchain image"

# sozud/saturn-compilers commit-pinned archive; the `-bin` subtree is the
# compiler itself (CPP/CC1/AS/AR/LD/OBJCOPY), the sibling tree is the SDK.
# `unzip` is not in the DOS base (the PSY-Q assets are tarballs), so it is
# installed here rather than widening every DOS image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-sh-elf unzip \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/saturn-cygnus /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/saturn.zip \
        "https://github.com/sozud/saturn-compilers/archive/af27f4aa6566c1b0fa5332b488e63d6ffd28bd48.zip" \
    && echo "f5460e3ea653a24fb011a94f2ce2c54b277877e60859ffc906b07dbbe6406595  /tmp/tools/saturn.zip" | sha256sum -c - \
    && unzip -q /tmp/tools/saturn.zip -d /tmp/tools \
    && cp -r /tmp/tools/saturn-compilers-af27f4aa6566c1b0fa5332b488e63d6ffd28bd48/cygnus-2.7-96Q3-bin/. \
        /opt/saturn-cygnus/ \
    && rm -rf /tmp/tools \
    && chmod +x /opt/saturn-cygnus/*.EXE \
    && ls /opt/saturn-cygnus/OBJCOPY.EXE

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

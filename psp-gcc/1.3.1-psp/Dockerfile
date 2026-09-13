# PSP GCC 1.3.1 — Sony PSP (allegrex) compiler, 32-bit i386 host binaries.
#
# Inherits the shared rebrew/base, which already carries the 32-bit runtime
# (wine32 pulled libc6:i386 and /lib/ld-linux.so.2): the driver, cc1/cc1plus
# and the vendor binutils in this asset are 32-bit i386 ELF binaries.
#
# The asset's layout is split and must be reassembled under the prefix the
# driver hard-codes (`/usr/local/psp/devkit`): `psp/bin` + `psp/include` +
# `psp/lib` (the SDK) live beside the compiler internals in `lib/gcc-lib`.
# Installing it anywhere else makes the driver report
# "installation problem, cannot exec `cc1'".  The driver also warns that
# `pspspecs`/`pspfixup`/`psplibgen` are absent — those scripts only matter
# for linking, and compiling is unaffected (verified).
#
# Build:  docker build -t rebrew/psp-gcc:1.3.1-psp psp-gcc/1.3.1-psp
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/psp-gcc:1.3.1-psp -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSP GCC 1.3.1" \
      org.opencontainers.image.description="PSP GCC 1.3.1 (mipsallegrex, PS1-family MIPS, 32-bit host) toolchain image"

# The tree lives under /opt like every other image here and is reached through
# the prefix the driver hard-codes, so the /opt contract and the vendor's
# expectation both hold (the symlink is what the driver's `bin/../lib/...`
# resolution walks through).
RUN mkdir -p /opt/psp-gcc-1.3.1 /tmp/psp \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/psp.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psp-gcc-1.3.1.tar.gz" \
    && echo "788b6d2c0ed920da6b1e5a350d23dd7ea05820526e23f9b5b967b3b238ea2e2e  /tmp/psp.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/psp.tar.gz -C /tmp/psp \
    && cp -r /tmp/psp/. /opt/psp-gcc-1.3.1/ \
    && cp -r /tmp/psp/psp/bin /tmp/psp/psp/include /opt/psp-gcc-1.3.1/ \
    && cp -r /tmp/psp/psp/lib/. /opt/psp-gcc-1.3.1/lib/ \
    && rm -rf /tmp/psp /tmp/psp.tar.gz \
    && chmod -R a+rX /opt/psp-gcc-1.3.1 \
    && mkdir -p /usr/local/psp \
    && ln -s /opt/psp-gcc-1.3.1 /usr/local/psp/devkit \
    && find /opt/psp-gcc-1.3.1 -name cc1 | grep .

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

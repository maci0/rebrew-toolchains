# Intel C++ Compiler 5.0.1 (build 010525Z) — win32, Windows PE under wine/wibo.
#
# Inherits the shared rebrew/base; this image installs the pinned Intel C++
# 5.0.1 tree (Bin/icl.exe + mcpcom.exe, Include/, lib/) and exposes `icl` as
# the entrypoint.  It compiles to Intel i386 COFF objects — the format MSVC 6
# and the old Windows toolchains consume.
#
# Note on provenance: decomp.me's own recipe fetches *two* files for this id —
# Microsoft C 6.0 (for the linker) and this Intel tree.  An earlier round here
# downloaded only the first and concluded the id was "a plain MSVC 6.0 tree";
# the Intel asset is separate and genuine (`icl.exe` reports "Intel(R) C++
# Compiler for 32-bit applications, Version 5.0.1   Build 010525Z").
#
# Build:  docker build -t rebrew/icc:5.0.1-010525z-win32 icc/5.0.1-010525z-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/icc:5.0.1-010525z-win32 -c f.c -o f.obj

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Intel C++ 5.0.1 (win32)" \
      org.opencontainers.image.description="Intel C++ Compiler 5.0.1 build 010525Z (i386 COFF, wine/wibo) toolchain image"

# The asset is flat (Bin/, Include/, lib/ at the root) — extract in place.
RUN mkdir -p /opt/icc-5.0.1 \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/icc.tar.gz \
        "https://github.com/bwrsandman/icc5.0.1.010525Z/releases/download/v1/icc5.0.1-010525z.tar.gz" \
    && echo "2661672232e8845004f40d8aaba15f19cde36750b72b3a864aa21f6a0d196564  /tmp/icc.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/icc.tar.gz -C /opt/icc-5.0.1 \
    && rm /tmp/icc.tar.gz \
    && chmod +x /opt/icc-5.0.1/Bin/*.exe \
    && ls /opt/icc-5.0.1/Bin/icl.exe

ENV REBREW_RUNNER=wibo

COPY icl-wrapper.sh /usr/local/bin/icl
RUN chmod +x /usr/local/bin/icl

ENTRYPOINT ["/usr/local/bin/icl"]

USER rebrew

# MSVC for Xbox 360 (PowerPC, 16.00.11886.00) — decomp.me id
# msvc_ppc_16.00.11886.00.
#
# Inherits the shared rebrew/base; this image extracts the X360 subtree
# (cl.exe driver with c1xx.dll/c2.dll/pdb tools, Windows PE + DLLs) from the
# pinned files.decomp.dev compilers zip and runs the MSVC-style driver
# through the shared wine/wibo dispatcher.
#
# Build:  docker build -t rebrew/msvc-ppc:16.00.11886-x360 msvc-ppc/16.00.11886-x360
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc-ppc:16.00.11886-x360 /c /O2 t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC PPC 16.00.11886 (Xbox 360)" \
      org.opencontainers.image.description="MSVC for Xbox 360 (PowerPC, 16.00.11886.00, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251015.zip" \
    && echo "491cb62317c7f3669ac283ae159e82e3c97a5713b78299571ba4cf023dc7e95e  /tmp/compilers.zip" | sha256sum -c - \
    && mkdir -p /opt/msvc-ppc-16.00.11886 \
    && unzip -q /tmp/compilers.zip 'X360/16.00.11886.00/*' -d /tmp/x360 \
    && cp -a /tmp/x360/X360/16.00.11886.00/. /opt/msvc-ppc-16.00.11886/ \
    && rm -rf /tmp/x360 /tmp/compilers.zip \
    && ls /opt/msvc-ppc-16.00.11886/cl.exe

# The `cl` wrapper: MSVC-style argv passes through verbatim; the driver's
# sibling DLLs (c1xx.dll, c2.dll, msvcp100.dll, ...) sit in the same
# directory, so wine resolves them without a WINEPATH.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'rebrew_run /opt/msvc-ppc-16.00.11886/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew

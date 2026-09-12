# MSVC 6.0 SP5 + Processor Pack — 32-bit PE compiler under wine
# (archaic-msvc/msvc600_sp5_vcpp).
#
# Inherits the shared rebrew/base; this image adds the MSVC 6.0 SP5
# command-line toolchain with the Visual C++ 6.0 Processor Pack applied: the
# code generator is replaced (c2.dll 13.00.9044.0), MASM 6.15 (ml.exe) lands
# in VC98/Bin, and the MMX/SSE/SSE2 intrinsic headers (mmintrin.h,
# xmmintrin.h, emmintrin.h, ...) land in VC98/Include.  cl.exe itself is
# unchanged (12.00.8804) and there is no /arch option: SSE/SSE2 code is
# written with the pack's intrinsics (or with MASM).  The pack applies to SP5,
# not SP6 (SP6 removes it).
#
# Build:  docker build -t rebrew/msvc:6.0-sp5-pp-win32 msvc/6.0-sp5-pp-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-sp5-pp-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 SP5 + Processor Pack (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp5 + VC6 Processor Pack (win32, wine) toolchain image"

# MSVC 6.0 SP5 + Processor Pack — archaic-msvc/msvc600_sp5_vcpp tarball
# (sha256-verified).  The extracted tree already has the pack applied, so no
# installer runs here (the pack's Vcpp.exe would patch in place).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp5_vcpp.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp5_vcpp/tar.gz/refs/heads/master" \
    && echo "1bbf177489054698fd5d29bf042692efdb5bec8719f9dc889b9b1c618c645991  /tmp/msvc600_sp5_vcpp.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc6.0-sp5-pp \
    && tar xzf /tmp/msvc600_sp5_vcpp.tar.gz -C /opt/msvc6.0-sp5-pp --strip-components=1 \
    && rm /tmp/msvc600_sp5_vcpp.tar.gz \
    # CL statically imports mspdb60.dll and only searches its own dir; the
    # product tree stashes it in the IDE dir (same relocation as the other
    # msvc6 images).
    && cp /opt/msvc6.0-sp5-pp/Common/MSDev98/Bin/MSPDB60.DLL /opt/msvc6.0-sp5-pp/VC98/Bin/ \
    # Fail the build if the tree is not the Processor Pack one: the SIMD
    # headers and MASM are the pack's markers.
    && ls /opt/msvc6.0-sp5-pp/VC98/Bin/CL.EXE \
          /opt/msvc6.0-sp5-pp/VC98/Bin/ml.exe \
          /opt/msvc6.0-sp5-pp/VC98/Include/xmmintrin.h \
          /opt/msvc6.0-sp5-pp/VC98/Include/emmintrin.h \
          /opt/msvc6.0-sp5-pp/VC98/PPreadme.htm

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc6.0-sp5-pp/VC98/Bin/CL.EXE <args>`.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'rebrew_run /opt/msvc6.0-sp5-pp/VC98/Bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

# Runtime drops back to the base image's non-root user.
USER rebrew

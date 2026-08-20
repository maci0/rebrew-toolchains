# MSVC 6.0-sp6 — 32-bit PE compiler under wine (archaic-msvc/msvc600_sp6).
#
# Inherits the shared rebrew/base; this image adds the MSVC 6.0-sp6
# command-line toolchain (archaic-msvc/msvc600_sp6 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:6.0-sp6-win32 toolchain/msvc/6.0-sp6-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-sp6-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp6 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp6 (win32, wine) toolchain image"

# MSVC 6.0-sp6 command-line toolchain — archaic-msvc/msvc600_sp6 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/6.0-sp6-win32).
RUN curl -sL -o /tmp/msvc600_sp6.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp6/tar.gz/refs/heads/master" \
    && echo "7c2aa3dd4c56b8054cc1ae0e00cd976005dd5b9b43ea8c33b22798a15c9c15c3  /tmp/msvc600_sp6.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc6.0-sp6 \
    && tar xzf /tmp/msvc600_sp6.tar.gz -C /opt/msvc6.0-sp6 --strip-components=1 \
    && rm /tmp/msvc600_sp6.tar.gz \
    # The repo stashes the PDB server DLL in the IDE dir (Common/MSDev98/Bin);
    # CL 12.00.8804 statically imports mspdb60.dll and only searches its own
    # dir — relocate the official file (same product tree).
    && cp /opt/msvc6.0-sp6/Common/MSDev98/Bin/MSPDB60.DLL /opt/msvc6.0-sp6/VC98/Bin/ \
    && ls /opt/msvc6.0-sp6/VC98/Bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc6.0-sp6/VC98/Bin/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc6.0-sp6/VC98/Bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

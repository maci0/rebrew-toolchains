# MSVC 1.0 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.0
# command-line tree from the committed msvc10.tar.xz (assembled from the
# WinWorldPC "Microsoft Visual C++ 1.0 Professional" 3.5" floppy set —
# 20×1.44MB, SZDD-compressed payload, 7z-extracted) and exposes the
# `cl10` entrypoint wrapper.  CL.EXE is a Phar Lap TNT DOS-extender (PE32
# like 1.5/1.52) — headless under DOSBox, producing 16-bit OMF.  Fully
# self-contained: no host files, no downloads.
#
# Build:  docker build -t rebrew/msvc:1.0-win16 toolchain/msvc/1.0-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.0-win16 /c test.c  (ENTRYPOINT is the cl10 wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.0 (win16, DOSBox) toolchain image"


# Vendored MSVC 1.0 command-line tree (BIN/INCLUDE/LIB at the tarball top).
COPY msvc10.tar.xz /tmp/msvc10.tar.xz
RUN mkdir -p /opt/msvc10 \
    && tar xJf /tmp/msvc10.tar.xz -C /opt/msvc10 \
    && rm /tmp/msvc10.tar.xz \
    && ls /opt/msvc10/BIN/CL.EXE

# The `cl10` wrapper (see cl10-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl10-wrapper.sh /usr/local/bin/cl10
RUN chmod +x /usr/local/bin/cl10

ENTRYPOINT ["/usr/local/bin/cl10"]

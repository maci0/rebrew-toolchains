# MSVC 1.52 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.52
# command-line tree from the committed msvc152.tar.xz (extracted from the
# archive.org en_vc152_202512 RAR SFX — the download itself is corrupt for
# 7z/unar, so the verified tree is vendored in-repo) and exposes the
# `cl16` entrypoint wrapper.  Fully self-contained: no host files, no
# downloads.
#
# Build:  docker build -t rebrew/msvc:1.52-win16 toolchain/msvc/1.52-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.52-win16 /c test.c  (ENTRYPOINT is the cl16 wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.52 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.52 (win16, DOSBox) toolchain image"


# Vendored MSVC 1.52 command-line tree (BIN/INCLUDE/LIB at the tarball top).
COPY msvc152.tar.xz /tmp/msvc152.tar.xz
RUN mkdir -p /opt/msvc152 \
    && tar xJf /tmp/msvc152.tar.xz -C /opt/msvc152 \
    && rm /tmp/msvc152.tar.xz \
    && ls /opt/msvc152/BIN/CL.EXE

# The `cl16` wrapper (see cl16-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl16-wrapper.sh /usr/local/bin/cl16
RUN chmod +x /usr/local/bin/cl16

ENTRYPOINT ["/usr/local/bin/cl16"]

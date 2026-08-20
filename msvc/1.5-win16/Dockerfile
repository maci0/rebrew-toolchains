# MSVC 1.5 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.5
# command-line tree from the committed msvc15.tar.xz (extracted from the
# archive.org en_vc152 item — the 1993 16-bit release; unlike the 1.52
# RAR SFX, this one extracts cleanly, so the verified tree is vendored
# in-repo) and exposes the `cl15` entrypoint wrapper.  Fully
# self-contained: no host files, no downloads.
#
# Build:  docker build -t rebrew/msvc:1.5-win16 toolchain/msvc/1.5-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.5-win16 /c test.c  (ENTRYPOINT is the cl15 wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.5 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.5 (win16, DOSBox) toolchain image"


# Vendored MSVC 1.5 command-line tree (BIN/INCLUDE/LIB at the tarball top).
COPY msvc15.tar.xz /tmp/msvc15.tar.xz
RUN mkdir -p /opt/msvc15 \
    && tar xJf /tmp/msvc15.tar.xz -C /opt/msvc15 \
    && rm /tmp/msvc15.tar.xz \
    && ls /opt/msvc15/BIN/CL.EXE

# The `cl15` wrapper (see cl15-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl15-wrapper.sh /usr/local/bin/cl15
RUN chmod +x /usr/local/bin/cl15

ENTRYPOINT ["/usr/local/bin/cl15"]

# MSVC 1.52 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.52
# command-line tree from the archaic-toolchains/msvc152 preservation
# repo (sha256-verified codeload — the verified extraction of the
# archive.org en_vc152_202512 RAR SFX, which is corrupt for 7z/unar) and
# exposes the `cl16` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:1.52-win16 toolchain/msvc/1.52-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.52-win16 /c test.c  (ENTRYPOINT is the cl16 wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.52 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.52 (win16, DOSBox) toolchain image"


# MSVC 1.52 command-line tree (BIN/INCLUDE/LIB at the repo top).
RUN curl -sL -o /tmp/msvc152.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc152/tar.gz/refs/heads/main" \
    && echo "18fbdb547aa6a6cdbb3a77b00b5453f6fd9ae2b543a1c4842552643384e4711b  /tmp/msvc152.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc152 \
    && tar xzf /tmp/msvc152.tar.gz -C /opt/msvc152 --strip-components=1 \
    && rm /tmp/msvc152.tar.gz \
    && ls /opt/msvc152/BIN/CL.EXE

# The `cl16` wrapper (see cl16-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl16-wrapper.sh /usr/local/bin/cl16
RUN chmod +x /usr/local/bin/cl16

ENTRYPOINT ["/usr/local/bin/cl16"]

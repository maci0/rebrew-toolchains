# MSVC 1.0 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.0
# command-line tree (archaic-toolchains/msvc10 tarball, assembled from the
# WinWorldPC "Microsoft Visual C++ 1.0 Professional" 3.5" floppy set —
# 20×1.44MB, SZDD-compressed payload — and sha256-pinned) and exposes the
# `cl10` entrypoint wrapper.  CL.EXE is a Phar Lap TNT DOS-extender (PE32
# like 1.5/1.52) — headless under DOSBox, producing 16-bit OMF.  Fully
# self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:1.0-win16 msvc/1.0-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.0-win16 /c test.c  (ENTRYPOINT is the cl10 wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.0 (win16, DOSBox) toolchain image"


# MSVC 1.0 command-line tree — archaic-toolchains/msvc10 tarball
# (sha256-verified; same source `rebrew toolchain vendor` assembles from).
RUN curl -fsSL -o /tmp/msvc10.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc10/tar.gz/refs/heads/main" \
    && echo "4858446b957fe327fedbb3a511316bebc060b72f22557a47397b905522668ce9  /tmp/msvc10.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc10 \
    && tar xzf /tmp/msvc10.tar.gz -C /opt/msvc10 --strip-components=1 \
    && rm /tmp/msvc10.tar.gz \
    && ls /opt/msvc10/BIN/CL.EXE

# The `cl10` wrapper (see cl10-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl10-wrapper.sh /usr/local/bin/cl10
RUN chmod +x /usr/local/bin/cl10

ENTRYPOINT ["/usr/local/bin/cl10"]

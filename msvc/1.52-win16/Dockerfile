# MSVC 1.52 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.52
# command-line tree (archaic-toolchains/msvc152 tarball, reconstructed from
# the archive.org en_vc152 media and sha256-pinned) and exposes the
# `cl16` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:1.52-win16 msvc/1.52-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:1.52-win16 /c test.c  (ENTRYPOINT is the cl16 wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.52 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.52 (win16, DOSBox) toolchain image"


# MSVC 1.52 command-line tree — archaic-toolchains/msvc152 tarball
# (sha256-verified; same source `rebrew toolchain vendor` assembles from).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc152.tar.gz \
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

# Runtime drops back to the base image's non-root user.
USER rebrew

# MSVC 1.5 — 16-bit compiler (Phar Lap TNT CL under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the MSVC 1.5
# command-line tree from the archaic-toolchains/msvc15 preservation repo
# (sha256-verified codeload — extracted from the archive.org en_vc152 item,
# the 1993 16-bit release) and exposes the `cl15` entrypoint wrapper.
# Fully self-contained: no host files.
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
RUN curl -sL -o /tmp/msvc15.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc15/tar.gz/refs/heads/main" \
    && echo "5cd1e4d9fd70fe97587fd3edfd0cebe3276e7b59ea5eb0848510f15c95d79aec  /tmp/msvc15.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc15 \
    && tar xzf /tmp/msvc15.tar.gz -C /opt/msvc15 --strip-components=1 \
    && rm /tmp/msvc15.tar.gz \
    && ls /opt/msvc15/BIN/CL.EXE

# The `cl15` wrapper (see cl15-wrapper.sh — uses wrapper-common.sh helpers).
COPY cl15-wrapper.sh /usr/local/bin/cl15
RUN chmod +x /usr/local/bin/cl15

ENTRYPOINT ["/usr/local/bin/cl15"]

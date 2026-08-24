# Turbo C++ 3.1 — 16-bit DOS compiler (TCC.EXE under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the Turbo C++ 3.1
# command-line tree (BIN/INCLUDE/LIB; archaic-toolchains/tc31 tarball,
# reconstructed from the archive.org `turboc3.1_202112` item and
# sha256-pinned) and exposes the `tcc` entrypoint wrapper.  Fully
# self-contained: no host files.
#
# Build:  docker build -t rebrew/borland:3.1-win16 borland/3.1-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:3.1-win16 -c test.c  (ENTRYPOINT is the tcc wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C++ 3.1 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C++ 3.1 (win16, DOSBox) toolchain image"


# Turbo C++ 3.1 command-line tree — archaic-toolchains/tc31 tarball
# (sha256-verified; same source `rebrew toolchain vendor` assembles from).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tc31.tar.gz \
        "https://codeload.github.com/archaic-toolchains/tc31/tar.gz/refs/heads/main" \
    && echo "3d534741ebdc31ffdceb87db8de3b7d494ad5c912b7cd1a4f326b4a94d0c2ba1  /tmp/tc31.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/tc31 \
    && tar xzf /tmp/tc31.tar.gz -C /opt/tc31 --strip-components=1 \
    && rm /tmp/tc31.tar.gz \
    && ls /opt/tc31/BIN/TCC.EXE

# The `tcc` wrapper: translate the POSIX-style argv into the DOSBox TCC
# invocation inside the mounted /work (source staged under an 8.3-safe
# name, object written back to /work).
COPY tc16-run.sh /usr/local/bin/tcc
RUN chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]

# Runtime drops back to the base image's non-root user.
USER rebrew

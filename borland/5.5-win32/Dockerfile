# Borland C++ 5.5 — 32-bit PE compiler under wine (archaic-toolchains/borlandc55).
#
# Inherits the shared rebrew/base; this image adds the Borland C++ 5.5
# free command-line tools (archaic-toolchains/borlandc55 repo tarball,
# sha256-pinned — byte-identical to the archive.org BorlandC55 tree) and
# exposes the `bcc` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/borland:5.5-win32 borland/5.5-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:5.5-win32 -c f.c  (ENTRYPOINT is the bcc wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.5 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.5 (win32, wine) toolchain image"


# Borland C++ 5.5 free command-line tools — archaic-toolchains/borlandc55 repo
# tarball (sha256-verified; bcc32.exe byte-identical to the archive.org
# BorlandC55 freecommandLinetools.exe payload this image previously extracted).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc55.tar.gz \
        "https://codeload.github.com/archaic-toolchains/borlandc55/tar.gz/refs/heads/main" \
    && echo "e9319c3904303ca4424cfed855b17837d10aa9653a3d8e6329d2adb3326392b0  /tmp/bcc55.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/bcc55 \
    && tar xzf /tmp/bcc55.tar.gz -C /opt/bcc55 --strip-components=1 \
    && rm /tmp/bcc55.tar.gz \
    && ls /opt/bcc55/Bin/bcc32.exe

# The `bcc` wrapper: bcc32 has no built-in include/lib path, so the
# vendored Include/Lib are passed explicitly (see bcc-wrapper.sh).
COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

# Runtime drops back to the base image's non-root user.
USER rebrew

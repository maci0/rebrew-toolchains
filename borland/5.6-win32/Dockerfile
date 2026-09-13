# Borland C++ 5.6 — the last Borland C++ release (bcc32, Windows PE).
#
# Inherits the shared rebrew/base; this image extracts BIN/, INCLUDE/ and
# LIB/ from the pinned earthsiege2/borland-cpp-ide preservation archive
# (commit 09bcecc81184) and exposes bcc32 as the entrypoint under the shared
# wine/wibo dispatcher, exactly like this repo's Borland C++ 5.5 image.
#
# 5.6 is a *different build* from 5.5 (`bcc32.exe` hashes differ:
# b6132ef6214568dc here vs e7f7853e8c71b120 for 5.5), so both are shipped.
# The archive also carries the IDE, HELP and SOURCE trees; only the
# command-line compiler tree is installed here.
#
# Build:  docker build -t rebrew/borland:5.6-win32 borland/5.6-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:5.6-win32 -c f.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.6 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.6 (win32, wine) toolchain image"

# earthsiege2/borland-cpp-ide at commit 09bcecc81184 (sha256-verified).  The
# archive is ~140 MB; only BIN/, INCLUDE/ and LIB/ are extracted.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc56.tar.gz \
        "https://codeload.github.com/earthsiege2/borland-cpp-ide/tar.gz/09bcecc81184" \
    && echo "8e5a93db99330b816646a14bdfa1c90d2e80a41810ce8c65f4942378cb621882  /tmp/bcc56.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/bcc56 \
    && tar xzf /tmp/bcc56.tar.gz -C /opt/bcc56 --strip-components=1 \
        borland-cpp-ide-09bcecc81184/BIN \
        borland-cpp-ide-09bcecc81184/INCLUDE \
        borland-cpp-ide-09bcecc81184/LIB \
    && rm /tmp/bcc56.tar.gz \
    && ls /opt/bcc56/BIN/BCC32.EXE

# The `bcc` wrapper: bcc32 has no built-in include/lib path, so the vendored
# Include/Lib are passed explicitly (see bcc-wrapper.sh).
COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

# Runtime drops back to the base image's non-root user.
USER rebrew

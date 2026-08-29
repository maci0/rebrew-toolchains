# IDO 5.3 — SGI MIPS compiler (N64) via ido-static-recomp, native Linux.
#
# Inherits the shared rebrew/base; this image adds the IDO 5.3 reimplementation
# (decompals/ido-static-recomp v1.2 release asset, sha256-pinned) and the `cc`
# entrypoint wrapper.  The ido-static-recomp binaries are statically
# recompiled IDO (from the original MIPS binaries via mips_to_c tooling) that
# run natively on Linux x86_64 — no wine/DOSBox needed.  Fully
# self-contained: no host files.
#
# Build:  docker build -t rebrew/ido:5.3-linux ido/5.3-linux
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:5.3-linux -c -o t.o t.c  (ENTRYPOINT is the cc wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 (MIPS, N64)" \
      org.opencontainers.image.description="IDO 5.3 reimplementation (MIPS-II big-endian, N64) toolchain image"

# IDO 5.3 reimplementation — decompals/ido-static-recomp v1.2 release asset
# (sha256-verified; the recomp binaries run natively on Linux x86_64, no
# wine).  The tarball has no top-level directory — extract in place.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido53.tar.gz \
        "https://github.com/decompals/ido-static-recomp/releases/download/v1.2/ido-5.3-recomp-linux.tar.gz" \
    && echo "ab5c741561f80913d58c8b074771f23941a3edd312505a8ebed6d1dfeb65e506  /tmp/ido53.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/ido/5.3 \
    && tar xzf /tmp/ido53.tar.gz -C /opt/ido/5.3 \
    && rm /tmp/ido53.tar.gz \
    && chmod +x /opt/ido/5.3/cc

# The `cc` wrapper: validate the source (common helper), then exec the IDO
# compiler with the original argv (POSIX-style: cc -c -o out.o src.c).  IDO
# resolves its sibling binaries (cfe, ugen, ...) relative to its own path.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec /opt/ido/5.3/cc "$@"' \
        > /usr/local/bin/cc \
    && chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

# Runtime drops back to the base image's non-root user.
USER rebrew

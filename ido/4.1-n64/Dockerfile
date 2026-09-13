# IDO 4.1 — SGI MIPS compiler (N64, original IRIX binaries under qemu-irix-4.0).
#
# Inherits the repository's Ubuntu-noble base (rebrew/base-dosemu) because the
# IDO 4.1 asset bundles `qemu-irix-4.0`, which needs GLIBC_2.38: Debian
# bookworm's 2.36 cannot load it (an earlier round proved the loader aborts on
# `__tunable_is_initialized (GLIBC_PRIVATE)` when trixie's libc is mixed into
# bookworm's).  Ubuntu noble's 2.39 satisfies it, so the same base that carries
# the DOS emulator carries this one too; dosemu2 is dormant here.
#
# The entrypoint is decomp.me's recipe: the emulator running the vendor IRIX
# `cc` with `-EL` (this is the little-endian N64 build), then the asset's own
# `ecoff_tool.py` converts the ECOFF output to an ELF relocatable.
#
# Build:  docker build -t rebrew/ido:4.1-n64 ido/4.1-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ido:4.1-n64 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 4.1 (N64, qemu-irix-4.0)" \
      org.opencontainers.image.description="IDO 4.1 (SGI MIPS, N64 little-endian, IRIX binaries under qemu-irix-4.0) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# decompme/compilers' `ido4.1` asset: the whole IRIX tool tree plus the
# emulator that can run it and the ECOFF converter.
RUN mkdir -p /opt/ido-4.1 \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido41.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ido4.1.tar.gz" \
    && echo "16008087602fe1a39cdd7880a3c6987891ddb594cce4416670f2e96456e9b4d4  /tmp/ido41.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/ido41.tar.gz -C /opt/ido-4.1 \
    && rm /tmp/ido41.tar.gz \
    && chmod +x /opt/ido-4.1/usr/bin/qemu-irix-4.0 \
    && /opt/ido-4.1/usr/bin/qemu-irix-4.0 --version 2>&1 | head -1 || true

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

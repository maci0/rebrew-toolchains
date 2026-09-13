# Borland C++ 2.0 (decomp.me repack) — the tree decomp.me serves as "bcc2.0".
#
# Inherits the shared rebrew/base; this image installs the pinned
# decompme/compilers `bcc2.0` repack and runs its DOS compiler under DOSBox
# through the shared 16-bit compile flow.  The source is staged as SRC.C and
# the object comes back as <source-stem>.OBJ.
#
# This is a *different build* from `borland/2.0-win16`, which this repo
# assembles from its own preserved media: the two trees' binaries do not
# match, so both are shipped and the community id maps here (see
# docs/PROVENANCE.md).
#
# Build:  docker build -t rebrew/borland:2.0-decompme-win16 borland/2.0-decompme-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:2.0-decompme-win16 t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 2.0 (decomp.me repack)" \
      org.opencontainers.image.description="Borland C++ 2.0 (decomp.me preservation repack, 16-bit DOS, DOSBox) toolchain image"

RUN mkdir -p /opt/bcc2.0dm /tmp/bcc \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc/bcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/bcc2.0.tar.gz" \
    && echo "6a8bb50e1d390e05ea8ef5ea076035eadda32eb1640b5b802538f2c3933565c3  /tmp/bcc/bcc.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/bcc/bcc.tar.gz -C /opt/bcc2.0dm \
    && rm -rf /tmp/bcc \
    && ls /opt/bcc2.0dm/bin/bcc.exe

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew

# Borland C++ 3.1 (decomp.me repack) — the tree decomp.me serves as "bcc3.1".
#
# Inherits the shared rebrew/base; this image installs the pinned
# decompme/compilers `bcc3.1` repack and runs its DOS compiler under DOSBox
# through the shared 16-bit compile flow.  The source is staged as SRC.C and
# the object comes back as <source-stem>.OBJ.
#
# This is a *different build* from `borland/3.1-win16`, which this repo
# assembles from its own preserved media: the two trees' binaries do not
# match, so both are shipped and the community id maps here (see
# docs/PROVENANCE.md).
#
# Build:  docker build -t rebrew/borland:3.1-decompme-win16 borland/3.1-decompme-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:3.1-decompme-win16 t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 3.1 (decomp.me repack)" \
      org.opencontainers.image.description="Borland C++ 3.1 (decomp.me preservation repack, 16-bit DOS, DOSBox) toolchain image"

RUN mkdir -p /opt/bcc3.1dm /tmp/bcc \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc/bcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/bcc3.1.tar.gz" \
    && echo "1fad5133fbe034f00e263e114993fbbcea5ff9ee061449b34e78704ed95af6fc  /tmp/bcc/bcc.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/bcc/bcc.tar.gz -C /opt/bcc3.1dm \
    && rm -rf /tmp/bcc \
    && ls /opt/bcc3.1dm/bin/bcc.exe

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew

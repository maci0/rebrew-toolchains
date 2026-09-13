# rebrew/base-noble — the Ubuntu-noble layer for toolchains Debian cannot host.
#
# Two families need a newer/other userland than `base/` (Debian bookworm):
# the 16-bit DOS toolchains (dosemu2 + dj64 are packaged only for Ubuntu —
# see base-dosemu) and the IRIX IDO images whose bundled `qemu-irix-4.0` needs
# GLIBC_2.38 (bookworm ships 2.36 and the loader aborts when trixie's libc is
# mixed in).  Both inherit this layer so the shared wrapper helpers and the
# unprivileged `rebrew` user exist in exactly one place.
#
# It deliberately installs nothing beyond the wrapper-common prerequisites:
# a family adds what *it* needs (dosemu2, libglib2.0 + python3, ...) so an
# image never carries a runtime it does not use.
#
# Build:  docker build -t rebrew/base-noble:1.0 base-noble

ARG HELPER_IMAGE=rebrew/base:1.0

FROM ${HELPER_IMAGE} AS helper

FROM ubuntu:noble

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base-noble (Ubuntu 24.04 + wrapper helpers)" \
      org.opencontainers.image.description="Ubuntu-noble layer for toolchains that need a newer glibc or non-Debian runtime packages"

COPY --from=helper /usr/local/lib/rebrew /usr/local/lib/rebrew

# Same unprivileged runtime user as base/ (uid/gid 1000, /work owned), so
# images built on any base behave identically for volumes and `USER rebrew`.
# Ubuntu's image already owns uid/gid 1000 as `ubuntu`, so rename it rather
# than adding a second account.
RUN groupmod -n rebrew ubuntu \
    && usermod -l rebrew -d /home/rebrew -m ubuntu \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gzip tar \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /work \
    && chown -R rebrew:rebrew /home/rebrew /work

ENV HOME=/home/rebrew

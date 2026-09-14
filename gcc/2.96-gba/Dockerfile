# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.96

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.96 Camelot (GBA)" \
      org.opencontainers.image.description="GCC 2.96 arm-elf (Camelot, GBA, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc296.tar.gz \
        "https://github.com/SBird1337/camelot-gcc/releases/download/2.96/gcc-2.96-20000731-armelf.tar.gz" \
    && echo "c0613784e1c3b228512db2abebdce1e7b8afc211dc904d9ae23b913fd9025af9  /tmp/gcc296.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/camelot-2.96 \
    && tar xzf /tmp/gcc296.tar.gz -C /opt/camelot-2.96 \
    && rm /tmp/gcc296.tar.gz \
    && ln -s /opt/camelot-2.96/usr/local/lib/gcc-lib /usr/local/lib/gcc-lib \
    && ln -s /opt/camelot-2.96/usr/local/arm-elf /usr/local/arm-elf \
    && /opt/camelot-2.96/usr/local/bin/arm-elf-gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew

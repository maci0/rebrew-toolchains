# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: saturn-cygnus-2.7-96Q3

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Saturn Cygnus 2.7-96Q3 (dosemu2)" \
      org.opencontainers.image.description="Cygnus 2.7-96Q3 (SH-2, Sega Saturn, DOS binaries under dosemu2) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-sh-elf unzip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/saturn-cygnus /tmp/tools && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/saturn.zip \
        "https://github.com/sozud/saturn-compilers/archive/af27f4aa6566c1b0fa5332b488e63d6ffd28bd48.zip" \
    && echo "f5460e3ea653a24fb011a94f2ce2c54b277877e60859ffc906b07dbbe6406595  /tmp/tools/saturn.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && unzip -q /tmp/tools/saturn.zip -d /tmp/tools \
    && cp -r /tmp/tools/saturn-compilers-af27f4aa6566c1b0fa5332b488e63d6ffd28bd48/cygnus-2.7-96Q3-bin/. /opt/saturn-cygnus/ \
    && rm -rf /tmp/tools \
    && chmod +x /opt/saturn-cygnus/*.EXE \
    && ls /opt/saturn-cygnus/OBJCOPY.EXE

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

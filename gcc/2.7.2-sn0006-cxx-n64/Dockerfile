# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.7.2-sn0006-cxx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 SN0006 C++ (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 SN0006 C++ (N64, PE/x86_32 pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/n64_sn272_0006.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/n64_sn272_0006.tar.gz" \
    && echo "1a35a875278f38bfc285c2bd80b782cec38859dedfd925d8b8a2f1733ba9acad  /tmp/tools/n64_sn272_0006.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-2.7.2-sn0006-cxx-n64 /tmp/tools \
    && tar xzf /tmp/tools/n64_sn272_0006.tar.gz -C /opt/gcc-2.7.2-sn0006-cxx-n64 \
    && rm -rf /tmp/tools \
    && chmod +x /opt/gcc-2.7.2-sn0006-cxx-n64/*.exe \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.7.2-sn0006-cxx-n64 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.7.2-sn0006-cxx-n64/psyq-obj-parser \
    && chmod +x /usr/local/bin/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

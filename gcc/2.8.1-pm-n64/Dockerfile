# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.8.1-pm

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.8.1 PM (N64)" \
      org.opencontainers.image.description="GCC 2.8.1 (papermario, N64, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/gcc.tar.gz \
        "https://github.com/pmret/gcc-papermario/releases/download/master/linux.tar.gz" \
    && echo "1156cf0d6a88a64c20e2a10fc9445d99cb9a38518f432b1669528dfa82ebb45f  /tmp/gcc.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/binutils.tar.gz \
        "https://github.com/pmret/binutils-papermario/releases/download/master/linux.tar.gz" \
    && echo "c3cd88db47ac41f78b557042c7e7ad47ac9c04cee6f0d1069a489c1c9e8c103c  /tmp/binutils.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/gcc-2.8.1-pm \
    && tar xzf /tmp/gcc.tar.gz -C /opt/gcc-2.8.1-pm \
    && tar xzf /tmp/binutils.tar.gz -C /opt/gcc-2.8.1-pm \
    && rm /tmp/gcc.tar.gz /tmp/binutils.tar.gz \
    && chmod +x /opt/gcc-2.8.1-pm/gcc /opt/gcc-2.8.1-pm/as \
    && /opt/gcc-2.8.1-pm/gcc --version

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew

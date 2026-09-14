# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-2.0-win16

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Open Watcom 2.0 (win16, native)" \
      org.opencontainers.image.description="Open Watcom 2.0 (win16, native) toolchain image"

ENV WATCOM=/opt/watcom \
    INCLUDE=/opt/watcom/h \
    PATH=/opt/watcom/binl:$PATH

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ow.tar.xz \
        "https://github.com/open-watcom/open-watcom-v2/releases/download/2026-09-01-Build/ow-snapshot.tar.xz" \
    && echo "bac354f3c75ffa49ff8d70a44e475de7e7c1823fff04b80c14787bd0792c9bdf  /tmp/ow.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/watcom \
    && tar xJf /tmp/ow.tar.xz --strip-components=1 -C /opt/watcom \
    && rm /tmp/ow.tar.xz \
    && ls /opt/watcom/binl/wcc

COPY wcc-wrapper.sh /usr/local/bin/wcc
RUN chmod +x /usr/local/bin/wcc

ENTRYPOINT ["/usr/local/bin/wcc"]

USER rebrew

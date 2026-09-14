# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msc-5.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Microsoft C 5.1 (DOS)" \
      org.opencontainers.image.description="Microsoft C 5.1 (16-bit DOS compiler, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msc/msc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/msc-5.1.tar.gz" \
    && echo "97ca199c20ad09629ae7be0a653faac56612e0e03ed700a92dbfb75958207311  /tmp/msc/msc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msc51 /tmp/msc \
    && tar xzf /tmp/msc/msc.tar.gz -C /opt/msc51 \
    && rm -rf /tmp/msc \
    && ls /opt/msc51/BIN/CL.EXE \
    && chmod +x /usr/local/bin/mscl

COPY msc51-wrapper.sh /usr/local/bin/mscl
RUN chmod +x /usr/local/bin/mscl

ENTRYPOINT ["/usr/local/bin/mscl"]

USER rebrew

# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ndk-r8e-4.4.3

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Android NDK r8e GCC 4.4.3 (x86)" \
      org.opencontainers.image.description="Android NDK r8e GCC 4.4.3 (i686-linux-android, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ndk/ndk.tar.bz2 \
        "https://github.com/decompme/compilers/releases/download/compilers/android-ndk-r8e-linux-x86_64-gcc-4.4.3.tar.bz2" \
    && echo "13c57455e63dfb17a98853792ba1063fc640605a4ef2db4ad33a654171f48267  /tmp/ndk/ndk.tar.bz2" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/ndk-r8e-4.4.3 /tmp/ndk \
    && tar xjf /tmp/ndk/ndk.tar.bz2 '*toolchains/x86-4.4.3/*' '*platforms/android-9/*' --wildcards -C /opt/ndk-r8e-4.4.3 \
    && rm -rf /tmp/ndk \
    && ls /opt/ndk-r8e-4.4.3/toolchains/x86-4.4.3/prebuilt/linux-x86_64/bin/i686-linux-android-gcc

COPY ndk-gcc-wrapper.sh /usr/local/bin/ndk-gcc
RUN chmod +x /usr/local/bin/ndk-gcc

ENTRYPOINT ["/usr/local/bin/ndk-gcc"]

USER rebrew

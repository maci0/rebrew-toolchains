# Android NDK r8e — GCC 4.4.3 x86 toolchain (decomp.me "ndk-r8e-gcc-4.4.3").
#
# Inherits the shared rebrew/base; this image installs the pinned decompme
# NDK repack and only the parts this toolchain needs: the GCC 4.4.3 x86
# cross-compiler and the API-9 x86 sysroot (the full NDK is ~4 GB unpacked).
# The driver is a native Linux x86_64 binary, so the wrapper execs it with
# the sysroot baked in, exactly as decomp.me's recipe does.
#
# Target: i686-linux-android (Android x86).
#
# Build:  docker build -t rebrew/ndk:r8e-4.4.3-android-x86 ndk/r8e-4.4.3-android-x86
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/ndk:r8e-4.4.3-android-x86 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Android NDK r8e GCC 4.4.3 (x86)" \
      org.opencontainers.image.description="Android NDK r8e GCC 4.4.3 (i686-linux-android, native x86_64) toolchain image"

# The source archive is a .tar.bz2 repack.
RUN apt-get update \
    && apt-get install -y --no-install-recommends bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ndk-r8e-4.4.3 /tmp/ndk \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/ndk/ndk.tar.bz2 \
        "https://github.com/decompme/compilers/releases/download/compilers/android-ndk-r8e-linux-x86_64-gcc-4.4.3.tar.bz2" \
    && echo "13c57455e63dfb17a98853792ba1063fc640605a4ef2db4ad33a654171f48267  /tmp/ndk/ndk.tar.bz2" | sha256sum -c - \
    && tar xjf /tmp/ndk/ndk.tar.bz2 -C /opt/ndk-r8e-4.4.3 --wildcards \
        '*toolchains/x86-4.4.3/*' '*platforms/android-9/*' \
    && rm -rf /tmp/ndk \
    && ls /opt/ndk-r8e-4.4.3/toolchains/x86-4.4.3/prebuilt/linux-x86_64/bin/i686-linux-android-gcc

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/ndk-r8e-4.4.3/toolchains/x86-4.4.3/prebuilt/linux-x86_64/bin/i686-linux-android-gcc --sysroot=/opt/ndk-r8e-4.4.3/platforms/android-9/arch-x86 "$@"' \
        > /usr/local/bin/ndk-gcc \
    && chmod +x /usr/local/bin/ndk-gcc

ENTRYPOINT ["/usr/local/bin/ndk-gcc"]

USER rebrew

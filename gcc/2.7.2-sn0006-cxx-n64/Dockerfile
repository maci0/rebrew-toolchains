# rebrew GCC 2.7.2 SN0006 C++ (N64) — decomp.me "gcc2.7.2sn0006-cxx".
#
# Inherits the shared rebrew/base and installs the decompme/compilers `n64_sn272_0006` tarball (cc1n64.exe, cc1pln64.exe, asn64.exe).
# decomp.me's recipe is a pipeline with no vendor driver in play, so the
# wrapper runs it — with the C++ cpp defines and cc1pln64.exe (the C++ front
# end in the same tree as the C one) — and psyq-obj-parser converts the Sony object.
#
# The host cpp needs g++: `cpp -lang-c++` enters C++ mode by running
# cc1plus, which the bare `cpp` package does not ship.
#
# The C++ ids exist because the C wrapper cannot serve them: piping a C++
# source through `cpp -lang-c` and cc1n64.exe produces an empty object with a
# success exit status, so C++ input needs this image.
#
# Build:  docker build -t rebrew/gcc:2.7.2-sn0006-cxx-n64 gcc/2.7.2-sn0006-cxx-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-sn0006-cxx-n64 -c f.C -o f.o

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

RUN mkdir -p /opt/gcc-2.7.2-sn0006-cxx-n64 /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/n64_sn272_0006.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/n64_sn272_0006.tar.gz" \
    && echo "1a35a875278f38bfc285c2bd80b782cec38859dedfd925d8b8a2f1733ba9acad  /tmp/tools/n64_sn272_0006.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/tools/n64_sn272_0006.tar.gz -C /opt/gcc-2.7.2-sn0006-cxx-n64 \
    && rm -rf /tmp/tools && chmod +x /opt/gcc-2.7.2-sn0006-cxx-n64/*.exe

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.7.2-sn0006-cxx-n64 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.7.2-sn0006-cxx-n64/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENV REBREW_RUNNER=wibo

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

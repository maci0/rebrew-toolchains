# rebrew Apple GCC 3.1, build 1041 (macOS) — decomp.me "gcc3-1041".
#
# Inherits the shared rebrew/base; this image installs the pinned
# powerpc-darwin-cross release (gcc3-1041.tar.gz) plus the revision-pinned
# convert_gas_syntax.py.  The Apple cc1 emits Darwin-flavoured assembler that
# GNU as rejects, so the `cc` wrapper runs decomp.me's three steps:
#
#   cc1 -quiet <flags> f.c -o f.s
#   python3 convert_gas_syntax.py f.s <stem> new > f_new.s
#   powerpc-linux-gnu-as f_new.s -o f.o
#
# Target: powerpc-apple-darwin (Apple GCC 3.1, build 1041).  Native x86_64 tools, no wine.
#
# Build:  docker build -t rebrew/gcc:3.1-1041-macos gcc/3.1-1041-macos
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:3.1-1041-macos -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Apple GCC 3.1, build 1041 (macOS)" \
      org.opencontainers.image.description="powerpc-apple-darwin (Apple GCC 3.1, build 1041) cross compiler (native x86_64) toolchain image"

# python3 runs the syntax converter; binutils-powerpc-linux-gnu supplies the
# assembler the converted output is fed to.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 binutils-powerpc-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-3.1-1041 /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/gcc3-1041.tar.gz \
        "https://github.com/ChrisNonyminus/powerpc-darwin-cross/releases/download/initial/gcc3-1041.tar.gz" \
    && echo "3ef1f2422e3cb9ede9a3f9c16d898c62550adde870ac58cb3b4e86689bdd702a  /tmp/tools/gcc3-1041.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/tools/gcc3-1041.tar.gz -C /opt/gcc-3.1-1041 \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-3.1-1041/convert_gas_syntax.py \
        "https://gist.githubusercontent.com/ChrisNonyminus/ec53837b151a65e4233fa53604de4549/raw/d7c6fc639310b938fa519e68a8f8d4909acba2ad/convert_gas_syntax.py" \
    && echo "8ad067bedef54c526774e6453f55ef7a2bedc93604bd7640a6a8a1cc64b3cda0  /opt/gcc-3.1-1041/convert_gas_syntax.py" | sha256sum -c - \
    && rm -rf /tmp/tools \
    && chmod +x /opt/gcc-3.1-1041/cc1 /opt/gcc-3.1-1041/convert_gas_syntax.py

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

# rebrew EGCS 1.1.2-4 (N64) — decomp.me "egcs_1.1.2-4".
#
# Inherits the shared rebrew/base and installs the AngheloAlf egcs_1.1.2-4 tarball (mips-linux-gcc driver, cc1, as, libgcc).
# The tree is a flat native dump whose driver resolves its tools through
# COMPILER_PATH, so the wrapper execs it directly.
#
# Build:  docker build -t rebrew/gcc:egcs-1.1.2-4-n64 gcc/egcs-1.1.2-4-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:egcs-1.1.2-4-n64 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EGCS 1.1.2-4 (N64)" \
      org.opencontainers.image.description="EGCS 1.1.2-4 (N64) (N64, native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends  \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-egcs-1.1.2-4 /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/egcs.tar.gz \
        "https://github.com/AngheloAlf/egcs_1.1.2-4/releases/download/latest/egcs_1.1.2-4.tar.gz" \
    && echo "c8d0adeecbe655db1631df5dea58781f4aa738f9762b907f58a6e70740d1815a  /tmp/tools/egcs.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/tools/egcs.tar.gz -C /opt/gcc-egcs-1.1.2-4 \
    && rm -rf /tmp/tools

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

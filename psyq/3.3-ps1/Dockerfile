# PSY-Q 3.3 — Sony PlayStation 1 SDK compiler, 1994 DOS binaries under dosemu2.
#
# Inherits rebrew/base-dosemu (Ubuntu + dosemu2 + the dj64 DPMI host) because
# CC1PSX.EXE is a 1994 DJGPP `go32` binary: DOSBox cannot load its stub, while
# dosemu2's emulated DPMI runs it.  The entrypoint runs decomp.me's pipeline —
# host cpp -> CC1PSX -> ASPSX -> psyq-obj-parser — with each DOS stage in its
# own dosemu2 session.
#
# NOTE: this image needs `--device /dev/kvm` at run time; the wrapper explains
#       that if the device is missing.
#
# Build:  docker build -t rebrew/psyq:3.3-ps1 psyq/3.3-ps1
# Invoke: docker run --rm --device /dev/kvm -v "$PWD":/work -w /work rebrew/psyq:3.3-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 3.3 (PlayStation 1, dosemu2)" \
      org.opencontainers.image.description="PSY-Q 3.3 (MIPS R3000, PS1, DOS binaries under dosemu2) toolchain image"

# PSY-Q 3.3 itself (mkst/esa's reconstruction of the SDK media) plus the
# decomp.me obj parser that converts the Sony object to an ELF relocatable.
RUN mkdir -p /opt/psyq-3.3 \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/mkst/esa/releases/download/psyq-binaries/psyq3.3.tar.gz" \
    && echo "6acc5bf3a2e406c35ec77b63f6f77986a2d61502906967f0f32ea75911e7f16f  /tmp/psyq.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/psyq.tar.gz --strip-components=1 -C /opt/psyq-3.3 \
    && rm /tmp/psyq.tar.gz \
    && chmod +x /opt/psyq-3.3/*.EXE

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/psyq-3.3 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/psyq-3.3/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

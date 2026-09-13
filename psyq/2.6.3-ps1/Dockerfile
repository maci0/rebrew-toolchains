# PSY-Q 2.6.3 — Sony PlayStation 1 SDK compiler, 1994 DOS binaries under dosemu2.
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
# Build:  docker build -t rebrew/psyq:2.6.3-ps1 psyq/2.6.3-ps1
# Invoke: docker run --rm --device /dev/kvm -v "$PWD":/work -w /work rebrew/psyq:2.6.3-ps1 -c t.c -o t.o

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 2.6.3 (PlayStation 1, dosemu2)" \
      org.opencontainers.image.description="PSY-Q 2.6.3 (MIPS R3000, PS1, DOS binaries under dosemu2) toolchain image"

# decomp.me's `psyq_263_221` repack of PSY-Q 2.6.3, which already
# carries the psyq-obj-parser this pipeline ends with.
RUN mkdir -p /opt/psyq-2.6.3 \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq_263_221.tar.gz" \
    && echo "082a57e28efe06dc75f1c8be4f2b73ffa65ad5b995c6c345cf67b8dcd19192c5  /tmp/psyq.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/psyq.tar.gz -C /opt/psyq-2.6.3 \
    && rm /tmp/psyq.tar.gz \
    && chmod +x /opt/psyq-2.6.3/*.EXE

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew

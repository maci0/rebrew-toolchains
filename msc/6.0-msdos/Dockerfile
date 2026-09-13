# Microsoft C 6.0 — 16-bit DOS compiler.
#
# Inherits the shared rebrew/base; this image installs the pinned
# decompme/compilers `msc600` tree (BIN/CL.EXE, INCLUDE/, LIB/) and runs it
# under DOSBox through the shared 16-bit compile flow, as the other DOS
# toolchains here do.  The source is staged as SRC.C and the object comes
# back as <source-stem>.OBJ (FAT-uppercased).
#
# MSC 6.0 is a different compiler from the 5.1 image here (different
# releases), and unlike the PSY-Q 3.x DOS tools its CL.EXE is a plain 16-bit
# DOS binary, so DOSBox runs it.
#
# Build:  docker build -t rebrew/msc:6.0-msdos msc/6.0-msdos
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msc:6.0-msdos t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Microsoft C 6.0 (DOS)" \
      org.opencontainers.image.description="Microsoft C 6.0 (16-bit DOS compiler, DOSBox) toolchain image"

RUN mkdir -p /opt/msc60 /tmp/msc \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/msc/msc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/msc600.tar.gz" \
    && echo "d918ee76b25f1e7c55fdcde6de37d4f47ad72e3e69c93e2323802fa951bd60c4  /tmp/msc/msc.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/msc/msc.tar.gz -C /opt/msc60 \
    && rm -rf /tmp/msc \
    && ls /opt/msc60/BIN/CL.EXE

COPY msc60-wrapper.sh /usr/local/bin/msc60
RUN chmod +x /usr/local/bin/msc60

ENTRYPOINT ["/usr/local/bin/msc60"]

USER rebrew

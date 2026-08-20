# Borland Delphi 1.0 — 16-bit NE compiler (DOS DPMI app under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the vendored Delphi 1.0
# toolchain (DCC.EXE + DELPHI.DSL + DPMI16BI.OVL + RTM.EXE + the RTL/VCL
# units) from the archaic-toolchains/delphi10 preservation repo
# (sha256-verified codeload; the RTL units come from the Quantum .PAK
# extraction) and the `dcc` entrypoint wrapper, which stages them into a
# fresh C: drive (a non-tmpfs sandbox — DOSBox 0.74-3 breaks on tmpfs) and
# runs DCC headless, writing the .EXE back to the mounted /work.  Fully
# self-contained: no host files.
#
# Build:  docker build -t rebrew/delphi:1.0-win16 toolchain/delphi/1.0-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/delphi:1.0-win16 hello.dpr  (ENTRYPOINT is the dcc wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Delphi 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Delphi 1.0 (win16, DOSBox) toolchain image"


# Vendored Delphi 1.0 toolchain: DCC.EXE, DELPHI.DSL, DPMI16BI.OVL, RTM.EXE
# and the RTL/VCL units (delphi-lib → /opt/delphi10/DELPHI/LIB).
RUN curl -sL -o /tmp/delphi10.tar.gz \
        "https://codeload.github.com/archaic-toolchains/delphi10/tar.gz/refs/heads/main" \
    && echo "24cd23f0ef555f3582eda27b4bb655e17215366b556dfaabd9f2ba5daf61b55e  /tmp/delphi10.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/delphi10 \
    && tar xzf /tmp/delphi10.tar.gz -C /opt/delphi10 --strip-components=1 \
    && rm /tmp/delphi10.tar.gz \
    && mkdir -p /opt/delphi10/DELPHI && mv /opt/delphi10/delphi-lib /opt/delphi10/DELPHI/LIB \
    && ls /opt/delphi10/DCC.EXE

COPY dcc-wrapper.sh /usr/local/bin/dcc
RUN chmod +x /usr/local/bin/dcc

ENTRYPOINT ["/usr/local/bin/dcc"]

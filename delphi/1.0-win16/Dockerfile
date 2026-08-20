# Borland Delphi 1.0 — 16-bit NE compiler (DOS DPMI app under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the vendored Delphi 1.0
# toolchain (DCC.EXE + DELPHI.DSL + DPMI16BI.OVL + RTM.EXE + the RTL/VCL
# units) from the committed delphi10.tar.xz (the RTL units come from the
# Quantum .PAK extraction — no public tarball) and the `dcc` entrypoint
# wrapper, which stages them into a fresh C: drive (a non-tmpfs sandbox —
# DOSBox 0.74-3 breaks on tmpfs) and runs DCC headless, writing the .EXE
# back to the mounted /work.  Fully self-contained: no host files, no
# downloads.
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
COPY delphi10.tar.xz /tmp/delphi10.tar.xz
RUN mkdir -p /opt/delphi10 \
    && tar xJf /tmp/delphi10.tar.xz -C /opt/delphi10 \
    && rm /tmp/delphi10.tar.xz \
    && mv /opt/delphi10/delphi-lib /opt/delphi10/DELPHI/LIB \
    && ls /opt/delphi10/DCC.EXE

COPY dcc-wrapper.sh /usr/local/bin/dcc
RUN chmod +x /usr/local/bin/dcc

ENTRYPOINT ["/usr/local/bin/dcc"]

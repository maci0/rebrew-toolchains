# Borland C++ 5.5 — 32-bit PE compiler under wine (free command-line tools).
#
# Inherits the shared rebrew/base; this image downloads the Borland C++ 5.5
# free command-line compiler from archive.org (BorlandC55 — an InstallShield
# self-extractor, sha256-pinned, extracted with 7z) and exposes the `bcc`
# entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/borland:5.5-win32 toolchain/borland/5.5-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:5.5-win32 -c f.c  (ENTRYPOINT is the bcc wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.5 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.5 (win32, wine) toolchain image"


# Borland C++ 5.5 free command-line tools: the archive.org zip holds an
# InstallShield self-extractor (freecommandLinetools.exe) whose payload
# (Bin/Include/Lib) 7z extracts directly.
RUN curl -sL -o /tmp/bcc55.zip \
        "https://archive.org/download/BorlandC55/Borland%20C%2B%2B%205.5.zip" \
    && echo "12affb942db2b9823292697faaa6f465b18c381ba347f9f4bf8efae6ff34cca1  /tmp/bcc55.zip" | sha256sum -c - \
    && unzip -q /tmp/bcc55.zip -d /tmp/bccsrc \
    && mkdir -p /opt/bcc55 \
    && (7z x -y "/tmp/bccsrc/freecommandLinetools.exe" -o/tmp/bccpay >/dev/null 2>&1 || true) \
    && mv /tmp/bccpay/Bin /opt/bcc55/Bin \
    && mv /tmp/bccpay/Include /opt/bcc55/Include \
    && mv /tmp/bccpay/Lib /opt/bcc55/Lib \
    && rm -rf /tmp/bcc55.zip /tmp/bccsrc /tmp/bccpay \
    && ls /opt/bcc55/Bin/bcc32.exe

# The `bcc` wrapper: bcc32 has no built-in include/lib path, so the
# vendored Include/Lib are passed explicitly (see bcc-wrapper.sh).
COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

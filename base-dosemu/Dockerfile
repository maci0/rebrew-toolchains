# rebrew/base-dosemu — the dosemu2 runtime layer for 16-bit DOS toolchains.
#
# Inherits base-noble (Ubuntu 24.04 + the shared wrapper helpers and user) and
# adds only what the DOS toolchains need; see base-noble for why a non-Debian
# base exists.
#
# The DOS-extended compilers of the early 1990s (PSY-Q 3.x's CC1PSX.EXE, Saturn
# Cygnus's CPP/CC1/AS) are DJGPP `go32` binaries.  DOSBox cannot load their
# stub — they exit silently with no object — so they need dosemu2 with the
# dj64 DPMI host, which is what decomp.me uses too.  Those packages exist only
# in Ubuntu PPAs (dosemu2/ppa and stsp-0/dj64), so this base is Ubuntu while
# `base/` is Debian; the shared wrapper helpers are copied out of `base/` so
# there is exactly one implementation of argument handling and error reporting.
#
# Every PPA package is pinned by sha256: the build never reads a PPA index, so
# a PPA rebuild cannot change what an image contains.
#
# NOTE: dosemu2 runs the guest CPU under KVM, so containers built FROM this
#       base must be run with `--device /dev/kvm`; rebrew_dosemu_run says so
#       if the device is missing.
#
# Build:  docker build -t rebrew/base-dosemu:1.0 base-dosemu

# Overridable so `PREFIX=registry/ ./build.sh` builds against the matching
# base-noble rather than the default namespace.
ARG NOBLE_IMAGE=rebrew/base-noble:1.0

FROM ${NOBLE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base-dosemu (dosemu2 + dj64 runtime layer)" \
      org.opencontainers.image.description="dosemu2/dj64 runtime base for 16-bit DOS toolchain images (needs --device /dev/kvm)"

# dosemu2's runtime libraries come from Ubuntu's archive (they are ordinary
# distro packages); only the PPA-only packages below are pinned.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates cpp curl dos2unix gzip libao4 libasound2t64 libb64-0d \
        libelf1t64 libfluidsynth3 libfontconfig1 libglib2.0-0t64 libgpm2 \
        libieee1284-3t64 libjansson4 libjson-c5 libreadline8t64 libsdl2-2.0-0 \
        libsdl2-ttf-2.0-0 libsearpc1t64 libseccomp2 libslang2 libslirp0 \
        libstdc++6 libx11-6 libxext6 python3 tar \
    && rm -rf /var/lib/apt/lists/*

# dosemu2 + the FreeDOS++ kernel (fdpp) + the dj64 DPMI host, from the two
# PPAs decomp.me's own backend uses.  apt installs the local files so their
# handful of Ubuntu-native dependencies resolve from the archive (the lists
# removed by the layer above are refreshed first).
RUN apt-get update \
    && mkdir -p /tmp/debs \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dosemu2.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/d/dosemu2/dosemu2_2.0~pre9-10295-4c9fe98ef+202609142054~ubuntu24.04.1_amd64.deb" \
    && echo "fc764ef92f98c152e2c4f753d4395a76eb900c5da23cc6d5d48815a119893e8d  /tmp/debs/dosemu2.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/fdpp.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/f/fdpp/fdpp_1.10-10002-1671-9282d8c+202605091902~ubuntu24.04.1_amd64.deb" \
    && echo "e1b2c238ef79c97ac588dfeec54cc8598890cd97e2e344dc4627258948d09d8d  /tmp/debs/fdpp.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdldr35.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/f/fdpp/libfdldr35_1.11-10003-1714-6fc57bc+202609081621~ubuntu24.04.1_amd64.deb" \
    && echo "a250e93e6d323d208a7cc2a998bcd03e9510831bf670d2da94eb5f2b6820f49d  /tmp/debs/libfdldr35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdpp35.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/f/fdpp/libfdpp35_1.11-10003-1714-6fc57bc+202609081621~ubuntu24.04.1_amd64.deb" \
    && echo "1baec8711043c75d1e29a4f260e926cb7343c9cc484f8c053970e0e0a7000a2a  /tmp/debs/libfdpp35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom64.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/c/comcom64/comcom64_0.5-0~202608251909+202608252240~ubuntu24.04.1_amd64.deb" \
    && echo "43e96d94b63beb0e9e14bb9304e4dc7d252bd743b7ac265555b2925e4d314eb5  /tmp/debs/comcom64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom32.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/c/comcom64/comcom32_0.5-0~202608251909+202608252240~ubuntu24.04.1_all.deb" \
    && echo "1065f09a596c111f4ea92c6b4efb3542364523765c378b0a1a3f64cdfacca888  /tmp/debs/comcom32.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dj64.deb \
        "https://ppa.launchpadcontent.net/stsp-0/dj64/ubuntu/pool/main/d/dj64dev/dj64_0.5-0~202608232226+202608240134~ubuntu24.04.1_amd64.deb" \
    && echo "c38d9355c742c15256d7ec78a2177438fdc6342ae8c0e4b6c982dac023cc8780  /tmp/debs/dj64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/djstub.deb \
        "https://ppa.launchpadcontent.net/stsp-0/dj64/ubuntu/pool/main/d/djstub/djstub_0.9-0~202608180717+202608181449~ubuntu24.04.1_all.deb" \
    && echo "84b11036b02322e2ce15089e9509d385f536b7cbc52034fc0edc434820e04a5b  /tmp/debs/djstub.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjstub64-0.deb \
        "https://ppa.launchpadcontent.net/stsp-0/dj64/ubuntu/pool/main/d/dj64dev/libdjstub64-0_0.5-0~202608232226+202608240134~ubuntu24.04.1_amd64.deb" \
    && echo "59e39e45c28b03aad80340db1e7b31e928aa24c705af7386c3bd2e93bd9a2bde  /tmp/debs/libdjstub64-0.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjdev64-0.deb \
        "https://ppa.launchpadcontent.net/stsp-0/dj64/ubuntu/pool/main/d/dj64dev/libdjdev64-0_0.5-0~202608232226+202608240134~ubuntu24.04.1_amd64.deb" \
    && echo "0ec1f660905dd24e0c8e529de80264c491a3bb917c6f3b11735ae5100447ae9a  /tmp/debs/libdjdev64-0.deb" | sha256sum -c - \
    && apt-get install -y --no-install-recommends /tmp/debs/dosemu2.deb /tmp/debs/fdpp.deb \
        /tmp/debs/libfdldr35.deb /tmp/debs/libfdpp35.deb /tmp/debs/comcom64.deb \
        /tmp/debs/comcom32.deb /tmp/debs/dj64.deb /tmp/debs/djstub.deb \
        /tmp/debs/libdjstub64-0.deb /tmp/debs/libdjdev64-0.deb \
    && rm -rf /tmp/debs /var/lib/apt/lists/* \
    && dpkg -s dosemu2 dj64 fdpp > /dev/null \
    && /usr/libexec/dosemu2/dosemu2.bin --version

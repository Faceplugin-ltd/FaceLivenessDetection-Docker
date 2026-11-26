# FaceLivenessDetection-Docker — liveness only
# Native libs are linux/amd64; image runs on any Docker host (Win/Mac/Linux).
# Before build: extract a runtime archive into ./lib/cpu/ (see lib/README.md)
# Bookworm is glibc 2.36; native SDK libs need GLIBC_2.38+ (Debian Trixie).
FROM --platform=linux/amd64 python:3.12-slim-trixie

RUN apt-get update -y && apt-get install -y --no-install-recommends \
        psmisc curl util-linux e2fsprogs libgomp1 libuuid1 zlib1g libusb-0.1-4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/facesdk

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py sdk.py license_ux.py http_body.py run.sh ./
COPY lib ./lib/

ENV LICENSE=/root/facesdk/license.txt
ENV LD_LIBRARY_PATH=/root/facesdk/lib/cpu
ENV PORT=8093
# Published port only works if the process listens on every interface.
ENV FACESDK_BIND_HOST=0.0.0.0
RUN chmod +x ./run.sh \
    && test -f ./lib/cpu/libFaceLivenessSDK.so \
    && test -f ./lib/cpu/libfacerec.so \
    && test -f ./lib/cpu/fal.fpk \
    && test -f ./lib/cpu/libonnxruntime.so \
    && test -f ./lib/cpu/libonnxruntime_providers_shared.so

CMD ["./run.sh"]
EXPOSE 8093

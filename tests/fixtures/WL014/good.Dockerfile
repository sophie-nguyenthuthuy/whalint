FROM debian:12-slim
WORKDIR /src
RUN make install

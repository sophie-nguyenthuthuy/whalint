FROM debian:12-slim
RUN cd /src && make install

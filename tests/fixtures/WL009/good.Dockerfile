FROM debian:12-slim
RUN curl -fsSL -o /tmp/install.sh https://get.example.com/install.sh && echo "d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26  /tmp/install.sh" | sha256sum -c - && sh /tmp/install.sh

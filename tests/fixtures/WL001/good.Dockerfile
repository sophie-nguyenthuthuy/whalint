FROM python:3.12-slim AS build
FROM ubuntu@sha256:6e9f67fa63b0323e9a1e587fd71c561ba48a034504fb804fd26fd8800039835d
FROM build

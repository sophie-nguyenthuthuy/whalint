FROM nginx:1.27-alpine
EXPOSE 8080
HEALTHCHECK --interval=30s CMD ["curl", "-f", "http://localhost:8080/health"]

# Specification: Nginx HTTPS & Reverse Proxy Integration

## Overview
Add Nginx to the existing `docker-compose.yml` to provide HTTPS support. Configure Nginx to act as a reverse proxy, listening on HTTPS (port 8000), routing requests to the backend service (http://127.0.0.1:8888/), handling API routes, and routing to the Authelia authentication service.

## Functional Requirements
1. **Docker Compose Integration**: Add an `nginx` service to the `docker-compose.yml` file.
2. **Nginx Configuration**:
   - Create a dedicated `./nginx` folder to store configuration files and certificates.
   - Configure Nginx to listen on port 8000 with HTTPS enabled.
   - Setup a reverse proxy block to forward root requests (`/` or as appropriate) and redirect URLs arriving at `https://127.0.0.1:8000/` to the backend service running at `http://127.0.0.1:8888/`.
   - Setup reverse proxy blocks for the API Route (`/api`) and the Authelia Route.
3. **SSL Certificate Generation**: Use OpenSSL to generate a self-signed certificate for local HTTPS development and store it in the `./nginx` folder structure.

## Non-Functional Requirements
- **Security**: Self-signed certificates should only be used for local development. Nginx should be configured with reasonably secure SSL protocols and ciphers.
- **Maintainability**: Nginx configuration should be clean and modular.

## Acceptance Criteria
- [ ] OpenSSL script/command generates a valid self-signed certificate in `./nginx/certs`.
- [ ] `docker-compose up` successfully starts Nginx alongside existing services.
- [ ] Accessing `https://127.0.0.1:8000/` correctly routes to the backend at `http://127.0.0.1:8888/`.
- [ ] Accessing `/api` and Authelia routes via Nginx works as expected.

## Out of Scope
- Provisioning production-grade certificates (e.g., Let's Encrypt).
- Configuring complex load balancing across multiple backend instances.
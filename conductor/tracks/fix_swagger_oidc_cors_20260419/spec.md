# Specification: Swagger UI OIDC CORS & Mixed Content Fix

## Overview
Swagger UI(HTTPS)에서 Authelia OIDC(HTTP) 호출 시 발생하는 `TypeError: Failed to fetch` (CORS 및 Mixed Content) 버그를 수정합니다. Nginx에 OIDC 엔드포인트 프록시를 추가하고, Authelia의 CORS 정책을 개방하며, FastAPI의 외부 노출 URL을 HTTPS 프록시 주소로 통일합니다.

## Functional Requirements
1. **Nginx Configuration**: `nginx/nginx.conf`에 Authelia OIDC 통신을 위한 `/api/oidc` 경로의 리버스 프록시(proxy_pass)를 추가합니다.
2. **Authelia Configuration**: `authelia/config/configuration.yml`에 Swagger UI(`https://127.0.0.1:8000`)에서의 접근을 허용하는 CORS 설정(allowed_origins)을 추가합니다.
3. **Environment Updates**: `.env` 파일 내 브라우저가 직접 접근하는 외부 노출 OIDC URL(`AUTHELIA_AUTHORIZATION_URL`, `AUTHELIA_TOKEN_URL` 등)을 모두 Nginx 프록시 주소(`https://127.0.0.1:8000`)로 업데이트합니다.

## Acceptance Criteria
- [ ] Nginx와 Authelia 컨테이너 재기동 후 오류 없이 정상 시작됩니다.
- [ ] Swagger UI에서 Authorize 버튼 클릭 시 CORS/Mixed Content 에러 없이 토큰이 성공적으로 교환되고 API 테스트가 가능합니다.
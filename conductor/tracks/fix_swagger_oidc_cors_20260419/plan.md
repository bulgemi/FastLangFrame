# Implementation Plan

## Phase 1: Configure Nginx & Authelia
- [ ] Task: Update Nginx and Authelia configurations
    - [ ] `nginx/nginx.conf` 파일에 `/api/oidc` 경로에 대한 리버스 프록시 설정을 추가하여 Authelia로 연결합니다.
    - [ ] `authelia/config/configuration.yml` 파일의 `identity_providers.oidc` 섹션에 `cors` 정책을 추가하여 `https://127.0.0.1:8000` 로부터의 요청을 허용합니다.
- [ ] Task: Conductor - User Manual Verification 'Configure Nginx & Authelia' (Protocol in workflow.md)

## Phase 2: Update Environment & Verify
- [ ] Task: Update environment and restart services
    - [ ] `.env` 파일의 외부 접근 OIDC URL들(`AUTHELIA_AUTHORIZATION_URL`, `AUTHELIA_TOKEN_URL`, `AUTHELIA_USERINFO_URL`)을 모두 Nginx의 HTTPS 주소(`https://127.0.0.1:8000/...`)로 업데이트합니다. (서버 내부 검증용인 `AUTHELIA_INTROSPECTION_URL`은 유지)
    - [ ] `docker compose restart nginx authelia` 명령어로 컨테이너를 재시작하여 변경된 설정을 반영합니다.
- [ ] Task: Conductor - User Manual Verification 'Update Environment & Verify' (Protocol in workflow.md)
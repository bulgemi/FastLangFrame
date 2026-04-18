# Authelia Setup for FastLangFrame

This guide provides instructions for setting up Authelia for FastLangFrame.

## 1. Configuration Files
The configuration files are located in `authelia/config/`.
- `configuration.yml`: Main Authelia configuration, including OIDC provider settings.
- `users_database.yml`: User database with the test user `user01`.

## 2. Docker Compose
Authelia is included in the `docker-compose.yml` file.

To start Authelia:
```bash
docker-compose up -d authelia
```

## 3. Test User
- **Username:** `user01`
- **Password:** `user01`

## 4. OIDC Client Details
- **Client ID:** `fastlangframe`
- **Client Secret:** `fastlangframe_secret` (The hash in configuration.yml corresponds to this plain text)
- **Scopes:** `openid`, `profile`, `email`, `groups`
- **Token Endpoint:** `http://localhost:9091/api/oidc/token`

## 5. Environment Configuration
Update your project's `.env` file with the following:
```env
AUTHELIA_TOKEN_URL=http://localhost:9091/api/oidc/token
AUTHELIA_CLIENT_ID=fastlangframe
AUTHELIA_CLIENT_SECRET=fastlangframe_secret
```

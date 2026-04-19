# Zitadel Setup for FastLangFrame

This guide provides instructions for setting up Zitadel for FastLangFrame.

## 1. Start Zitadel
Zitadel is included in the `docker-compose.yml` file.

To start Zitadel and its database:
```bash
docker-compose up -d zitadel
```

The initial setup might take a minute as the `zitadel-init` container runs the database setup.

## 2. Access Zitadel Console
- **URL:** `http://localhost:8080/ui/console`
- **Initial Login:**
    - **Username:** `zitadel-admin@zitadel.localhost`
    - **Password:** `Password123!` (You will be prompted to change this on first login)

## 3. Configure FastLangFrame
1.  **Create an Organization:** (Or use the default one)
2.  **Create a Project:** Name it `FastLangFrame`.
3.  **Create an Application:**
    -   **Type:** `Native` (or Web, but Native works well for CLI/Scripts)
    -   **Auth Method:** `None` (for Public) or `Post` (for Secret). For our OAuth2 Password Grant, we'll use `Post`.
    -   **Grant Types:** Enable `Password`.
    -   **Redirect URIs:** `http://localhost:8000/docs/oauth2-redirect`
4.  **Get Client Details:**
    -   Copy the `Client ID`.
    -   Generate and copy a `Client Secret`.

## 4. Create a Test User
1.  Navigate to **Users** in your organization.
2.  Click **Create**.
3.  **Username:** `user01`
4.  **Password:** `user01`
5.  Ensure the user is active and has no mandatory MFA for local testing.

## 5. Environment Configuration
Update your project's `.env` file with the following:
```env
ZITADEL_TOKEN_URL=http://localhost:8080/oauth/v2/token
ZITADEL_CLIENT_ID=<Your_Client_ID>
ZITADEL_CLIENT_SECRET=<Your_Client_Secret>
```

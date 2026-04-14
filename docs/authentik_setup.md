# Authentik Setup for FastLangFrame OAuth2 Password Flow

This guide provides instructions for setting up Authentik to work with the FastLangFrame FastAPI backend using the OAuth2 Resource Owner Password Credentials Grant.

## 1. Access Authentik Admin Interface
-   Navigate to `http://localhost:9000/if/admin/`.
-   Login with your admin credentials.

## 2. Create an OAuth2/OpenID Provider
1.  Navigate to **Resources** > **Providers**.
2.  Click **Create**.
3.  Select **OAuth2/OpenID Provider**.
4.  Configure the following fields:
    -   **Name:** `FastLangFrame OAuth2 Provider`
    -   **Authentication flow:** `default-authentication-flow`
    -   **Authorization flow:** `default-provider-authorization-implicit-confirmation`
    -   **Client Type:** `Confidential`
    -   **Client ID:** (Copy this for use in `.env`)
    -   **Client Secret:** (Copy this for use in `.env`)
    -   **Allowed Redirect URIs:** `http://localhost:8000/docs/oauth2-redirect` (Optional, useful for Swagger UI)
5.  Under **Advanced protocol settings**, ensure that the **Resource Owner Password Credentials Grant** is enabled (or handled by the flow).

## 3. Create a FastLangFrame Application
1.  Navigate to **Resources** > **Applications**.
2.  Click **Create**.
3.  Configure the following fields:
    -   **Name:** `FastLangFrame`
    -   **Slug:** `fastlangframe`
    -   **Provider:** Select the `FastLangFrame OAuth2 Provider` created in the previous step.

## 4. Create a Test User
1.  Navigate to **Directory** > **Users**.
2.  Click **Create**.
3.  Configure the following fields:
    -   **Username:** `user01`
    -   **Name:** `Test User 01`
4.  Once the user is created, click on `user01` in the list.
5.  Click the **Change Password** button.
6.  Set the password to `user01`.

## 5. Environment Configuration
Update your project's `.env` file with the following (using the values from Step 2):
```env
AUTHENTIK_CLIENT_ID=<Your_Client_ID>
AUTHENTIK_CLIENT_SECRET=<Your_Client_Secret>
AUTHENTIK_TOKEN_URL=http://localhost:9000/application/o/token/
```

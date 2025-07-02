# Assignment 1: Securing and Monitoring an Authenticated Flask App

## ✅ Overview

This project combines two previous labs:
- **Lab 1**: Flask app with SSO login via Auth0
- **Lab 2**: Flask app with logging, Azure deployment, KQL detection & alerting

In this assignment, we integrate both functionalities into a production-ready Flask app that supports:
- Auth0-based user authentication
- Logging of login and protected route access
- Detection of excessive access via KQL
- Azure alerts for suspicious activity

---

## 🔐 Auth0 Setup

### 1. Create Auth0 Application

1. Go to [Auth0](https://auth0.com/) and log in.
2. Create a Regular Web Application.
3. Set the following in settings:
   - **Callback URL**: `https://<your-app>.azurewebsites.net/callback`
   - **Logout URL**: `https://<your-app>.azurewebsites.net`

### 2. .env.example

```env
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
AUTH0_DOMAIN=
APP_SECRET_KEY=

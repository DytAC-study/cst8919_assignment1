# CST8919 Assignment 1 - Secure Flask App with Azure Monitoring

Youtube Video: https://youtu.be/Ik4s3eZpKSg

## 🔒 Project Overview

This project demonstrates how to build and monitor a **Flask web application** on **Azure App Service**, with authentication via **Auth0**, structured user activity logging, real-time **KQL threat detection**, and **Azure Monitor alerting**.

It fulfills the goal of **detecting suspicious login activity** such as excessive access to protected resources and triggering alerts to security stakeholders.

## 🔧 Application Architecture & Logic

### Key Endpoints

- `/` - Public home page
- `/login` - Redirects to Auth0 login page
- `/callback` - Handles Auth0 redirect, stores user session
- `/protected` - Protected route requiring login
- `/logout` - Clears session and redirects to Auth0 logout

### Authentication

- Implemented via **Auth0**
- Uses Flask sessions and `@requires_auth` decorator to protect routes
- Minimal user info (ID, name, email) stored in session to prevent cookie bloat

### Logging Logic

On each access to `/protected`, the app logs a structured JSON message containing:

- `timestamp`, `activity_type`, `client_ip`, `user_agent`
- Authenticated `user_id`, `email`, `name`
- `route` details

Logged as: `INFO - USER_ACTIVITY: {json}`

## 🔹 Azure Services Used & Setup

### Azure CLI Setup

#### 1. **Create Resource Group**

```
az group create -n cst8919-a1 -l canadacentral
```

#### 2. **Create App Service Plan**

```
az appservice plan create -g cst8919-a1 -n cst8919-plan --sku B1 --is-linux
```

#### 3. **Create Web App**

```
az webapp create -g cst8919-a1 -p cst8919-plan -n cst8919-du000086 --runtime "PYTHON|3.10" --deployment-local-git
```

#### 4. **Configure Startup Command**

```
az webapp config set -g cst8919-a1 -n cst8919-du000086 \
  --startup-file "pip install -r requirements.txt && gunicorn --bind=0.0.0.0 app:app"
```

#### 5. **Deploy via ZIP**

```
az webapp deployment source config-zip -g cst8919-a1 -n cst8919-du000086 --src ../app.zip
```

## 🔍 KQL Threat Detection Logic

We define suspicious behavior as a user accessing more than 10 times in 15 minutes.

### KQL Query

```
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription contains "USER_ACTIVITY"
| where ResultDescription contains "protected_route_access"
| extend LogData = parse_json(substring(ResultDescription, indexof(ResultDescription, "{")))
| where isnotempty(LogData.user_id)
| summarize AccessCount = count() by
    user_id = tostring(LogData.user_id),
    email = tostring(LogData.email),
    bin(TimeGenerated, 15m)
| where AccessCount > 10
| project TimeGenerated, user_id, email, AccessCount
| order by AccessCount desc
```

### Why this logic?

- Normal usage involves 1–2 requests to `/protected`
- More than 10 requests could indicate:
  - Bot/script attack
  - Credential stuffing
  - Session replay
- We mitigate it by sending a low-severity (Level 3) alert for visibility

## 🚨 Azure Monitor Alert Configuration

### Step 1: Create Action Group

- Name: `cst8919-security-alerts`
- Action Type: Email
- Recipient: your personal/institutional email

### Step 2: Create Alert Rule

- **Signal type**: Log
- **Query**: (use KQL above)
- **Time window**: 15 min
- **Frequency**: 5 min
- **Threshold**: greater than 0 results
- **Severity**: 3 (Low)
- **Action Group**: select previously created group

### Test Case

Run the following from your browser after login:

```
for (let i = 0; i < 20; i++) fetch('/protected');
```

Wait a few minutes, verify:

- ✉️ Email received
- ☁️ Alert visible in Azure Portal > Alerts

## 🌐 Auth0 Configuration

| Field               | Value                                               |
| ------------------- | --------------------------------------------------- |
| Login URI           | https://cst8919-du000086.azurewebsites.net/         |
| Callback URL        | https://cst8919-du000086.azurewebsites.net/callback |
| Logout URL          | https://cst8919-du000086.azurewebsites.net/         |
| Allowed Web Origins | https://cst8919-du000086.azurewebsites.net/         |

> Note: Always use HTTPS and avoid trailing slashes on the callback/login/logout URLs.



## 🌟 Highlights

- Real-world simulation of an internal security monitoring pipeline
- Combines Flask + Auth0 + Azure Logs + KQL + Alerts
- Demonstrates full lifecycle: dev > deploy > observe > respond


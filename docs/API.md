# MarzGuard API Reference

Base URL: `/api/v1`

## Authentication

### POST /auth/token
Login and obtain JWT token.

**Request** (form-urlencoded):
- `username`: admin username
- `password`: admin password
- `grant_type`: "password"

**Response**:
```json
{"access_token": "...", "token_type": "bearer"}
```

All other endpoints require `Authorization: Bearer <token>` header.

---

## Users

### GET /users
List users with active IP counts. Paginated.
- Query: `page`, `page_size`, `search`

### GET /users/{username}
Get user detail with active IPs.

### PUT /users/{username}
Update user IP config.
- Body: `{"ip_limit": 3, "policy_id": 1, "is_exempt": false, ...}`

### POST /users/{username}/disable
Manually disable user via Marzban.

### POST /users/{username}/enable
Manually re-enable user via Marzban.

### POST /users/sync
Sync user list from Marzban panel.

---

## Policies

### GET /policies
List all policies.

### POST /policies
Create a new policy.
- Body: `{"name": "Premium", "default_ip_limit": 5, ...}`

### PUT /policies/{policy_id}
Update a policy.

### DELETE /policies/{policy_id}
Delete a policy.

### POST /policies/batch-assign
Assign a policy to multiple users.
- Body: `{"usernames": ["user1", "user2"], "policy_id": 1}`

---

## Dashboard

### GET /dashboard/summary
Summary statistics.

### GET /dashboard/live
Full IP tracking snapshot.

---

## Settings

### GET /settings
Get global settings.

### PUT /settings
Update global settings.
- Body: `{"settings": {"default_ip_limit": "3", ...}}`

---

## Audit Log

### GET /logs
Query audit logs. Paginated.
- Query: `page`, `page_size`, `event_type`, `username`

---

## Webhooks

### POST /webhooks/marzban
Receive Marzban webhook events.
- Header: `X-Webhook-Secret`

---

## WebSocket

### WS /ws/live
Real-time dashboard updates.
- Query: `token` (JWT token)
- Sends JSON snapshot every 5 seconds

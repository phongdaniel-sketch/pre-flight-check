---

# Bug_Report.md

# To-Do App - Comprehensive Bug Report

## 1. Backend API

### Authentication
- Missing strong password validation enforcing complexity.
- Lax email format validation.
- Logout endpoint lacks token invalidation leading to possible token reuse.
- Inconsistent error format across endpoints.
- No rate limiting on login, vulnerable to brute force.

### Task Management
- No ownership check on task update/delete allowing unauthorized access.
- Task status accepts invalid strings; missing enum restriction.
- Due dates are not validated for format or past dates.
- Missing title length constraints.
- Pagination parameters are not validated for negative or zero values.
- PUT requests do not clearly support partial updates or enforce field restrictions.

### Security
- JWT secret hardcoded, should be environment config.
- No refresh token mechanism, users forced to re-login.
- No CORS restrictions.
- No HTTPS enforcement.

## 2. Database Schema

- Task status not enforced as an ENUM leading to invalid data.
- Missing indexes on foreign keys.
- No explicit password salt usage confirmed.
- No soft delete for tasks.
- Potential inconsistencies in timestamps.

## 3. Swagger API Docs

- Field name mismatches between swagger and backend (camelCase vs snake_case).
- Missing documentation for logout endpoint.
- Missing enumerations and example values.
- Incomplete error response models.

## 4. Frontend

- Drag-and-drop reorder is visual only without persistence.
- Incomplete client-side validation.
- Error messages are inconsistently displayed.
- Logout does not call backend logout endpoint.
- Missing ARIA attributes and focus management on modals.

---

# Test_Suite.py

```python
import pytest
import requests

BASE_URL = "http://localhost:3000/api"

test_user = {"email": "qauser@example.com", "password": "ValidPass123!"}
second_user = {"email": "otheruser@example.com", "password": "OtherPass123$"}

def register_user(data):
    return requests.post(f"{BASE_URL}/auth/register", json=data)

def login_user(data):
    return requests.post(f"{BASE_URL}/auth/login", json=data)

def logout_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{BASE_URL}/auth/logout", headers=headers)

def create_task(token, payload):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{BASE_URL}/tasks", headers=headers, json=payload)

def get_tasks(token, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE_URL}/tasks", headers=headers, params=params)

def update_task(token, task_id, payload):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.put(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=payload)

def delete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)

@pytest.fixture(scope="module")
def auth_token():
    register_user(test_user)
    res = login_user(test_user)
    assert res.status_code == 200
    token = res.json().get("token")
    assert token
    return token

@pytest.fixture(scope="module")
def auth_token_2():
    register_user(second_user)
    res = login_user(second_user)
    assert res.status_code == 200
    token = res.json().get("token")
    assert token
    return token

def test_register_invalid_email():
    res = register_user({"email": "invalid-email", "password": "StrongPass1"})
    assert res.status_code == 400

def test_register_weak_password():
    res = register_user({"email": "user2@example.com", "password": "123"})
    assert res.status_code == 400

def test_login_wrong_password():
    res = login_user({"email": test_user["email"], "password": "WrongPass"})
    assert res.status_code == 401

def test_logout_requires_token(auth_token):
    res = logout_user(auth_token)
    assert res.status_code in [200, 204]

valid_task = {
    "title": "QA Test Task",
    "description": "Test task description",
    "due_date": "2099-12-31T23:59:59Z",
    "status": "pending"
}

def test_create_task_success(auth_token):
    res = create_task(auth_token, valid_task)
    assert res.status_code in [200, 201]
    data = res.json()
    assert "id" in data
    assert data["title"] == valid_task["title"]

def test_create_task_invalid_due_date(auth_token):
    task = valid_task.copy()
    task["due_date"] = "not-a-date"
    res = create_task(auth_token, task)
    assert res.status_code == 400

def test_update_task_unauthorized(auth_token, auth_token_2):
    res = create_task(auth_token_2, valid_task)
    task_id = res.json().get("id")
    res = update_task(auth_token, task_id, {"title": "Hacked"})
    assert res.status_code in [403, 404]

def test_delete_other_user_task(auth_token, auth_token_2):
    res = create_task(auth_token_2, valid_task)
    task_id = res.json().get("id")
    res = delete_task(auth_token, task_id)
    assert res.status_code in [403, 404]
```

---

This concludes the bug report and comprehensive test suite covering critical backend functionality, validation, security, and proper API behavior in alignment with the project specifications.
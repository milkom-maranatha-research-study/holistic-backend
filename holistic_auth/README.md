# API Documentation

## Authentication

### Login API
- `POST /login/`
  <br/><br/>HTTP Header

  ```
  Authorization: Basic <base64.encode(${username} + ':' + ${password})>
  ```

  Response data has the following format:
  ```json
  {
    "expiry": "2022-11-19T03:04:24.308384Z",
    "token": "514e0c50c56669a89309053912cb5d208f04117efbed77388141640b15dfc031",
    "user": {
      "id": 3,
      "username": "panji",
      "email": "panji@mail.com",
      "first_name": "Panji",
      "last_name": "Update",
      "is_active": false,
      "date_joined": "2022-11-15T08:58:17Z"
    }
  }
  ```

## Logout API
Any request to the Logout API, needs to provide the following HTTP Header.

```
Authorization: Token <AUTH TOKEN>
```

- `POST /logout/`
- `POST /logout-all/`

Response code is `204` with and have no response.

## Account API
### Create Account
- `POST /accounts/`
  <br/><br/>Request Body:

  ```json
  {
    "username": "panji",
    "email": "panji@mail.com",
    "password": "TestPassword",
    "first_name": "Panji",
    "last_name": "Test"
  }
  ```

  Response data has the following format:
  ```json
  {
    "id": 1,
    "username": "panji",
    "email": "panji@mail.com",
    "first_name": "Panji",
    "last_name": "Test",
    "is_active": false,
    "date_joined": "2022-11-15T08:58:17Z"
  }
  ```

### Get Account
- `GET /accounts/me/`

  Response data has the following format:
  ```json
  {
    "id": 1,
    "username": "panji",
    "email": "panji@mail.com",
    "first_name": "Panji",
    "last_name": "Test",
    "is_active": false,
    "date_joined": "2022-11-15T08:58:17Z"
  }
  ```

### Update Account
- `PUT /accounts/me/`
  <br/><br/>Request Body:

  ```json
  {
    "email": "panji@mail.com",
    "first_name": "Panji",
    "last_name": "Test",
    "new_password": "NewPassword",
    "old_password": "OldPassword"
  }
  ```

  Response data has the following format:
  ```json
  {
    "id": 1,
    "username": "panji",
    "email": "panji@mail.com",
    "first_name": "Panji",
    "last_name": "Test",
    "is_active": false,
    "date_joined": "2022-11-15T08:58:17Z"
  }
  ```

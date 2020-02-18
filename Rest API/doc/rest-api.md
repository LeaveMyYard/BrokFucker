# Rest API for BrokFucker (16.02.2020)

## General API Information
* The base endpoint is: **https://127.0.0.1:5000**
* All endpoints return either a JSON object or array.
* All time and timestamp related fields are in **human-readable format**.

## HTTP Return Codes

* HTTP `4XX` return codes are used for malformed requests;
  the issue is on the sender's side.
* HTTP `403` return code is used when the WAF Limit (Web Application Firewall) has been violated.
* HTTP `429` return code is used when breaking a request rate limit.
* HTTP `418` return code is used when an IP has been auto-banned for continuing to send requests after receiving `429` codes.
* HTTP `5XX` return codes are used for internal errors; the issue is on
  server's side.
  It is important to **NOT** treat this as a failure operation; the execution status is
  **UNKNOWN** and could have been a success.

## Error Codes
* Any endpoint can return an ERROR

Sample Payload below:
```javascript
{
  "code": -1121,
  "msg": "Invalid symbol."
}
```
* Specific error codes and messages are defined in [Errors Codes](./errors.md).

## General Information on Endpoints
* All parameters must be sent as a `query string` with content type `application/json`.
* Parameters may be sent in any order.

## Endpoint Examples
Here is a step-by-step example of how to send a vaild signed payload from the
Windows command line using `curl`.

### Example for POST /api/v1/register
* **request json:** {'email': 'test@gmail.com', 'password': 'qwerty1312'}

* **curl command:**

    ```
    [windows] curl -i -H "Content-Type: application/json" -X POST -d "{""email"":""test@gmail.com"", ""password"":""qwerty1312""}"  http://127.0.0.1:5000/api/v1/register
    ```

Notice that standart Windows console support only "" brackets.
Also, double bracket symbol inside double brackets should be called as two brackets.
So, "{""email"":""test@gmail.com"", ""password"":""qwerty1312""}" would be '{"email":"test@gmail.com", "password":"qwerty1312"}'

### Example for GET /api/v1/getUserData with autentification

Some endpoints are protected and only accessed with user/moderator autentification.
It requires you to provide username(email) and password in request.
Users are all the registered accounts, but moderator is a specific account type.
From now, all the Endpoints will be described with **Level**, that could be Public, User and Moderator.
If you don't provide account data (if needed), it is not correct or it has not enough privileges, you will recieve an error.

* **request json:** NONE

* **curl command:**

    ```
    [windows] curl -u test@gmail.com:qwerty1312 -i http://localhost:5000/api/v1/getUserData
    ```

# API Endpoints
## Public endpoints

### Test connectivity
```
GET /api/v1/ping
```
Test connectivity to the Rest API.

**Level:**
Public

**Parameters:**
NONE

**Response:**
```javascript
{}
```

### Create new account
```
POST /api/v1/register
```
Registrate a new account.

**Level:**
Public

**Parameters:**
email: string
password: string

**Response:**
```javascript
{
  'msg': 'New user created'
}
```

## User endpoints

### Get user data
```
GET /api/v1/ping
```
Load all main user data.

**Level:**
User

**Parameters:**
NONE

**Response:**
```javascript
  'email': 'test@gmail.com',
  'type': 'user',
  'registration_date': '',
  'name': null,
  'phone_number': null
```

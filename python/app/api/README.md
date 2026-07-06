# CropSense AI - API Documentation

## Authentication Endpoints

All authentication endpoints are available under `/auth`

### User Registration

**POST** `/auth/signup`

Register a new user with Amazon Cognito.

**Request Body:**
```json
{
  "username": "farmer123",
  "password": "SecurePass123!",
  "email": "farmer@example.com",
  "phone_number": "+919876543210",
  "full_name": "John Farmer",
  "user_type": "farmer"
}
```

**Response:**
```json
{
  "user_sub": "cognito-user-id",
  "user_confirmed": false,
  "message": "User registered successfully. Please verify your email/phone.",
  "code_delivery_details": {
    "Destination": "f***@example.com",
    "DeliveryMedium": "EMAIL"
  }
}
```

### Confirm Registration

**POST** `/auth/confirm-signup`

Confirm user registration with verification code.

**Request Body:**
```json
{
  "username": "farmer123",
  "confirmation_code": "123456"
}
```

### Resend Verification Code

**POST** `/auth/resend-code`

Resend verification code to user.

**Request Body:**
```json
{
  "username": "farmer123"
}
```

### Sign In

**POST** `/auth/signin`

Authenticate user and get JWT tokens.

**Request Body:**
```json
{
  "username": "farmer123",
  "password": "SecurePass123!"
}
```

**Response (Success):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "id": 1,
    "username": "farmer123",
    "email": "farmer@example.com",
    "full_name": "John Farmer",
    "user_type": "farmer"
  }
}
```

**Response (MFA Required):**
```json
{
  "challenge": "SMS_MFA",
  "session": "session-token",
  "message": "MFA code sent to your phone. Please verify."
}
```

### Verify MFA

**POST** `/auth/verify-mfa`

Complete sign-in with MFA code.

**Request Body:**
```json
{
  "username": "farmer123",
  "session": "session-token",
  "mfa_code": "123456"
}
```

### Refresh Token

**POST** `/auth/refresh`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "username": "farmer123",
  "refresh_token": "refresh-token-here"
}
```

### Forgot Password

**POST** `/auth/forgot-password`

Initiate password reset flow.

**Request Body:**
```json
{
  "username": "farmer123"
}
```

### Confirm Forgot Password

**POST** `/auth/confirm-forgot-password`

Complete password reset with verification code.

**Request Body:**
```json
{
  "username": "farmer123",
  "confirmation_code": "123456",
  "new_password": "NewSecurePass123!"
}
```

## User Profile Endpoints

All user profile endpoints are available under `/users` and require authentication.

### Get Current User Profile

**GET** `/users/me`

Get current authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "farmer123",
    "cognito_user_id": "cognito-user-id",
    "email": "farmer@example.com",
    "phone_number": "+919876543210",
    "full_name": "John Farmer",
    "user_type": "farmer",
    "is_active": true,
    "is_verified": true,
    "language_preference": "en",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "cognito_attributes": {
    "sub": "cognito-user-id",
    "email": "farmer@example.com",
    "email_verified": "true",
    "phone_number": "+919876543210",
    "phone_number_verified": "true",
    "name": "John Farmer"
  }
}
```

### Update User Profile

**PUT** `/users/me`

Update current user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Updated Farmer",
  "email": "newemail@example.com",
  "phone_number": "+919876543211",
  "language_preference": "hi"
}
```

### Change Password

**POST** `/users/me/change-password`

Change user password (when logged in).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "previous_password": "OldPassword123!",
  "proposed_password": "NewPassword123!"
}
```

### Sign Out

**POST** `/users/me/signout`

Sign out current user (invalidate all tokens).

**Headers:**
```
Authorization: Bearer <access_token>
```

### Enable MFA

**POST** `/users/me/mfa/enable`

Enable SMS-based MFA for current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Disable MFA

**POST** `/users/me/mfa/disable`

Disable SMS-based MFA for current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Get User by ID

**GET** `/users/{user_id}`

Get public user profile by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": 400,
    "message": "Error description",
    "type": "error_type"
  }
}
```

Common error codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Authentication Flow

1. **Registration**: User signs up → Receives verification code → Confirms account
2. **Sign In**: User signs in → Receives JWT tokens (or MFA challenge)
3. **MFA (if enabled)**: User enters MFA code → Receives JWT tokens
4. **API Access**: Include access token in Authorization header for protected endpoints
5. **Token Refresh**: Use refresh token to get new access token when expired

## Testing with cURL

### Sign Up
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!",
    "email": "test@example.com",
    "phone_number": "+919876543210",
    "full_name": "Test Farmer",
    "user_type": "farmer"
  }'
```

### Sign In
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "password": "TestPass123!"
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

## Interactive API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## Farm Management Endpoints

All farm management endpoints are available under `/farms` and require farmer authentication.

### Create Farm

**POST** `/farms/`

Register a new farm for the current farmer.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Green Valley Farm",
  "state": "Punjab",
  "district": "Ludhiana",
  "village": "Khanna",
  "total_area_acres": 10.5,
  "location_lat": 30.7046,
  "location_lng": 76.7179,
  "plots": [
    {
      "name": "North Plot",
      "area_acres": 5.0,
      "soil_type": "clay",
      "irrigation_type": "canal"
    },
    {
      "name": "South Plot",
      "area_acres": 5.5,
      "soil_type": "loamy",
      "irrigation_type": "borewell"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "farmer_id": 1,
  "name": "Green Valley Farm",
  "state": "Punjab",
  "district": "Ludhiana",
  "village": "Khanna",
  "total_area_acres": 10.5,
  "location_lat": 30.7046,
  "location_lng": 76.7179,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "plots": [
    {
      "id": 1,
      "farm_id": 1,
      "name": "North Plot",
      "area_acres": 5.0,
      "soil_type": "clay",
      "irrigation_type": "canal",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "farm_id": 1,
      "name": "South Plot",
      "area_acres": 5.5,
      "soil_type": "loamy",
      "irrigation_type": "borewell",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get My Farms

**GET** `/farms/`

Get all farms for the current farmer.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100, max: 100)

**Response:**
```json
{
  "farms": [
    {
      "id": 1,
      "farmer_id": 1,
      "name": "Green Valley Farm",
      "state": "Punjab",
      "district": "Ludhiana",
      "village": "Khanna",
      "total_area_acres": 10.5,
      "location_lat": 30.7046,
      "location_lng": 76.7179,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Get Farm Details

**GET** `/farms/{farm_id}`

Get detailed farm information including all plots.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Update Farm

**PUT** `/farms/{farm_id}`

Update farm profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Farm Name",
  "total_area_acres": 12.0,
  "village": "New Village"
}
```

### Delete Farm

**DELETE** `/farms/{farm_id}`

Delete farm (soft delete - marks as inactive).

**Headers:**
```
Authorization: Bearer <access_token>
```

## Plot Management Endpoints

### Add Plot to Farm

**POST** `/farms/{farm_id}/plots`

Add a new plot to an existing farm.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "East Plot",
  "area_acres": 3.5,
  "soil_type": "sandy",
  "irrigation_type": "drip"
}
```

**Soil Types:**
- `clay` - Clay soil
- `sandy` - Sandy soil
- `loamy` - Loamy soil
- `silt` - Silt soil
- `peat` - Peat soil
- `mixed` - Mixed soil types

**Irrigation Types:**
- `rain-fed` - Rain-fed irrigation
- `canal` - Canal irrigation
- `borewell` - Borewell irrigation
- `drip` - Drip irrigation
- `sprinkler` - Sprinkler irrigation
- `mixed` - Mixed irrigation types

### Get Farm Plots

**GET** `/farms/{farm_id}/plots`

Get all plots for a specific farm.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "plots": [
    {
      "id": 1,
      "farm_id": 1,
      "name": "North Plot",
      "area_acres": 5.0,
      "soil_type": "clay",
      "irrigation_type": "canal",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Update Plot

**PUT** `/farms/{farm_id}/plots/{plot_id}`

Update plot information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Plot Name",
  "area_acres": 5.5,
  "soil_type": "loamy"
}
```

### Delete Plot

**DELETE** `/farms/{farm_id}/plots/{plot_id}`

Delete plot (soft delete - marks as inactive).

**Headers:**
```
Authorization: Bearer <access_token>
```

## Testing Farm Management with cURL

### Create Farm
```bash
curl -X POST http://localhost:8000/farms/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm",
    "state": "Punjab",
    "district": "Ludhiana",
    "total_area_acres": 10.0,
    "plots": [
      {
        "name": "Plot 1",
        "area_acres": 5.0,
        "soil_type": "clay",
        "irrigation_type": "canal"
      }
    ]
  }'
```

### Get My Farms
```bash
curl -X GET http://localhost:8000/farms/ \
  -H "Authorization: Bearer <access_token>"
```

### Add Plot
```bash
curl -X POST http://localhost:8000/farms/1/plots \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Plot",
    "area_acres": 3.0,
    "soil_type": "loamy",
    "irrigation_type": "drip"
  }'
```

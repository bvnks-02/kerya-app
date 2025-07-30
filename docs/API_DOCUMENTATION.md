# Kerya App API Documentation

## Overview

The Kerya App API provides a comprehensive set of endpoints for managing property rentals, user accounts, bookings, and more. This document details all available endpoints, request/response formats, and authentication requirements.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.kerya.com`

## Authentication

### JWT Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Token Types

- **Access Token**: Short-lived (30 minutes) for API access
- **Refresh Token**: Long-lived (7 days) for token renewal

## Common Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_1234567890"
}
```

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_1234567890",
  "details": {
    // Additional error details
  }
}
```

## HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## Authentication Endpoints

### Register User

**POST** `/api/v1/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "phone": "+1234567890",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "client"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully. Please verify your email and phone number.",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "phone": "+1234567890",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "client",
      "is_verified": false,
      "rating": 0.0,
      "points": 100,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Login User

**POST** `/api/v1/auth/login`

Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "phone": "+1234567890",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "client",
      "is_verified": true,
      "rating": 4.5,
      "points": 250,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Refresh Token

**POST** `/api/v1/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "new_refresh_token_here",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Logout User

**POST** `/api/v1/auth/logout`

Invalidate current session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Verify Email

**POST** `/api/v1/auth/verify-email`

Verify user email address.

**Request Body:**
```json
{
  "email": "user@example.com",
  "token": "verification_token_here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email verified successfully"
}
```

### Verify Phone

**POST** `/api/v1/auth/verify-phone`

Verify user phone number.

**Request Body:**
```json
{
  "phone": "+1234567890",
  "token": "verification_token_here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Phone number verified successfully"
}
```

### Resend Verification

**POST** `/api/v1/auth/resend-verification`

Resend verification codes.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification codes sent successfully"
}
```

---

## User Management Endpoints

### Get User Profile

**GET** `/api/v1/users/profile`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "client",
    "is_verified": true,
    "profile_image": "https://s3.amazonaws.com/kerya-profiles/user1.jpg",
    "rating": 4.5,
    "points": 250,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Update User Profile

**PUT** `/api/v1/users/profile`

Update current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1234567890",
  "profile_image": "https://s3.amazonaws.com/kerya-profiles/user1.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Smith",
    "user_type": "client",
    "is_verified": true,
    "profile_image": "https://s3.amazonaws.com/kerya-profiles/user1.jpg",
    "rating": 4.5,
    "points": 250,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### Get User Points

**GET** `/api/v1/users/points`

Get current user's points and history.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Points retrieved successfully",
  "data": {
    "points": 250,
    "history": [
      {
        "id": 1,
        "amount": 100,
        "type": "registration_bonus",
        "description": "Registration bonus",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": 2,
        "amount": 50,
        "type": "booking_earned",
        "description": "Points earned from booking",
        "created_at": "2024-01-16T14:20:00Z"
      }
    ]
  }
}
```

### Change Password

**POST** `/api/v1/users/change-password`

Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## Property Endpoints

### List Properties

**GET** `/api/v1/properties`

Get list of properties with search and filtering.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `size` (integer): Items per page (default: 20, max: 50)
- `search` (string): Search term
- `wilaya` (string): Location filter
- `property_type` (string): Property type filter
- `min_price` (number): Minimum price per night
- `max_price` (number): Maximum price per night
- `guests` (integer): Number of guests
- `check_in` (date): Check-in date (YYYY-MM-DD)
- `check_out` (date): Check-out date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "message": "Properties retrieved successfully",
  "data": {
    "properties": [
      {
        "id": 1,
        "host": {
          "id": 2,
          "first_name": "Jane",
          "last_name": "Smith",
          "rating": 4.8
        },
        "title": "Beautiful Studio in Algiers",
        "description": "Modern studio apartment in the heart of Algiers...",
        "property_type": "studio",
        "price_per_night": 75.00,
        "wilaya": "Algiers",
        "address": "123 Main Street, Algiers",
        "latitude": 36.7538,
        "longitude": 3.0588,
        "max_guests": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "rating": 4.5,
        "review_count": 12,
        "images": [
          "https://s3.amazonaws.com/kerya-properties/prop1_1.jpg",
          "https://s3.amazonaws.com/kerya-properties/prop1_2.jpg"
        ],
        "is_available": true,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Get Property Details

**GET** `/api/v1/properties/{property_id}`

Get detailed information about a specific property.

**Response:**
```json
{
  "success": true,
  "message": "Property details retrieved successfully",
  "data": {
    "id": 1,
    "host": {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "rating": 4.8,
      "response_rate": 95,
      "response_time": "2 hours"
    },
    "title": "Beautiful Studio in Algiers",
    "description": "Modern studio apartment in the heart of Algiers...",
    "property_type": "studio",
    "price_per_night": 75.00,
    "wilaya": "Algiers",
    "address": "123 Main Street, Algiers",
    "latitude": 36.7538,
    "longitude": 3.0588,
    "max_guests": 2,
    "bedrooms": 1,
    "bathrooms": 1,
    "amenities": [
      "WiFi",
      "Kitchen",
      "Air Conditioning",
      "Washing Machine"
    ],
    "house_rules": [
      "No smoking",
      "No pets",
      "No parties"
    ],
    "rating": 4.5,
    "review_count": 12,
    "images": [
      {
        "id": 1,
        "url": "https://s3.amazonaws.com/kerya-properties/prop1_1.jpg",
        "is_primary": true
      },
      {
        "id": 2,
        "url": "https://s3.amazonaws.com/kerya-properties/prop1_2.jpg",
        "is_primary": false
      }
    ],
    "availability": {
      "next_available": "2024-02-01",
      "calendar": [
        {
          "date": "2024-01-20",
          "available": false,
          "price": null
        },
        {
          "date": "2024-01-21",
          "available": true,
          "price": 75.00
        }
      ]
    },
    "is_available": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Create Property

**POST** `/api/v1/properties`

Create a new property listing (hosts only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Beautiful Studio in Algiers",
  "description": "Modern studio apartment in the heart of Algiers...",
  "property_type": "studio",
  "price_per_night": 75.00,
  "wilaya": "Algiers",
  "address": "123 Main Street, Algiers",
  "latitude": 36.7538,
  "longitude": 3.0588,
  "max_guests": 2,
  "bedrooms": 1,
  "bathrooms": 1,
  "amenities": [
    "WiFi",
    "Kitchen",
    "Air Conditioning"
  ],
  "house_rules": [
    "No smoking",
    "No pets"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Property created successfully",
  "data": {
    "id": 1,
    "title": "Beautiful Studio in Algiers",
    "description": "Modern studio apartment in the heart of Algiers...",
    "property_type": "studio",
    "price_per_night": 75.00,
    "wilaya": "Algiers",
    "address": "123 Main Street, Algiers",
    "latitude": 36.7538,
    "longitude": 3.0588,
    "max_guests": 2,
    "bedrooms": 1,
    "bathrooms": 1,
    "is_available": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Update Property

**PUT** `/api/v1/properties/{property_id}`

Update property information (hosts only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Updated Studio Title",
  "description": "Updated description...",
  "price_per_night": 80.00,
  "max_guests": 3
}
```

**Response:**
```json
{
  "success": true,
  "message": "Property updated successfully",
  "data": {
    "id": 1,
    "title": "Updated Studio Title",
    "description": "Updated description...",
    "price_per_night": 80.00,
    "max_guests": 3,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### Delete Property

**DELETE** `/api/v1/properties/{property_id}`

Delete property listing (hosts only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Property deleted successfully"
}
```

### Upload Property Images

**POST** `/api/v1/properties/{property_id}/images`

Upload images for a property.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
Form data with image files
```

**Response:**
```json
{
  "success": true,
  "message": "Images uploaded successfully",
  "data": {
    "images": [
      {
        "id": 1,
        "url": "https://s3.amazonaws.com/kerya-properties/prop1_1.jpg",
        "is_primary": true
      },
      {
        "id": 2,
        "url": "https://s3.amazonaws.com/kerya-properties/prop1_2.jpg",
        "is_primary": false
      }
    ]
  }
}
```

---

## Booking Endpoints

### Create Booking

**POST** `/api/v1/bookings`

Create a new booking.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "property_id": 1,
  "check_in_date": "2024-02-01",
  "check_out_date": "2024-02-05",
  "guests_count": 2,
  "special_requests": "Early check-in if possible"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Booking created successfully",
  "data": {
    "id": 1,
    "property": {
      "id": 1,
      "title": "Beautiful Studio in Algiers",
      "images": ["https://s3.amazonaws.com/kerya-properties/prop1_1.jpg"]
    },
    "host": {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-05",
    "guests_count": 2,
    "total_price": 300.00,
    "status": "pending",
    "payment_status": "pending",
    "special_requests": "Early check-in if possible",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### List User Bookings

**GET** `/api/v1/bookings`

Get list of user's bookings.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer): Page number
- `size` (integer): Items per page
- `status` (string): Booking status filter

**Response:**
```json
{
  "success": true,
  "message": "Bookings retrieved successfully",
  "data": {
    "bookings": [
      {
        "id": 1,
        "property": {
          "id": 1,
          "title": "Beautiful Studio in Algiers",
          "images": ["https://s3.amazonaws.com/kerya-properties/prop1_1.jpg"]
        },
        "host": {
          "id": 2,
          "first_name": "Jane",
          "last_name": "Smith"
        },
        "check_in_date": "2024-02-01",
        "check_out_date": "2024-02-05",
        "guests_count": 2,
        "total_price": 300.00,
        "status": "confirmed",
        "payment_status": "paid",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 5,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Get Booking Details

**GET** `/api/v1/bookings/{booking_id}`

Get detailed booking information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Booking details retrieved successfully",
  "data": {
    "id": 1,
    "property": {
      "id": 1,
      "title": "Beautiful Studio in Algiers",
      "description": "Modern studio apartment...",
      "images": ["https://s3.amazonaws.com/kerya-properties/prop1_1.jpg"],
      "address": "123 Main Street, Algiers"
    },
    "host": {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "phone": "+1234567890"
    },
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-05",
    "guests_count": 2,
    "total_price": 300.00,
    "status": "confirmed",
    "payment_status": "paid",
    "special_requests": "Early check-in if possible",
    "payment_details": {
      "payment_method": "credit_card",
      "transaction_id": "txn_123456789",
      "paid_at": "2024-01-15T10:35:00Z"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### Confirm Booking (Host)

**PUT** `/api/v1/bookings/{booking_id}/confirm`

Confirm a booking (hosts only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Booking confirmed successfully",
  "data": {
    "id": 1,
    "status": "confirmed",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

### Cancel Booking

**PUT** `/api/v1/bookings/{booking_id}/cancel`

Cancel a booking.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "reason": "Change of plans"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Booking cancelled successfully",
  "data": {
    "id": 1,
    "status": "cancelled",
    "refund_amount": 300.00,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

## Review Endpoints

### Create Review

**POST** `/api/v1/reviews`

Create a review for a completed booking.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "booking_id": 1,
  "rating": 5,
  "comment": "Excellent stay! The apartment was clean and well-located."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Review created successfully",
  "data": {
    "id": 1,
    "booking_id": 1,
    "property_id": 1,
    "rating": 5,
    "comment": "Excellent stay! The apartment was clean and well-located.",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Property Reviews

**GET** `/api/v1/properties/{property_id}/reviews`

Get reviews for a specific property.

**Query Parameters:**
- `page` (integer): Page number
- `size` (integer): Items per page
- `rating` (integer): Filter by rating

**Response:**
```json
{
  "success": true,
  "message": "Reviews retrieved successfully",
  "data": {
    "reviews": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "first_name": "John",
          "last_name": "Doe",
          "profile_image": "https://s3.amazonaws.com/kerya-profiles/user1.jpg"
        },
        "rating": 5,
        "comment": "Excellent stay! The apartment was clean and well-located.",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "summary": {
      "average_rating": 4.5,
      "total_reviews": 12,
      "rating_distribution": {
        "5": 8,
        "4": 3,
        "3": 1,
        "2": 0,
        "1": 0
      }
    },
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 12,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

---

## Post Endpoints

### Create Post

**POST** `/api/v1/posts`

Create a client post for property requests.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Looking for 2-bedroom apartment in Algiers",
  "description": "I need a 2-bedroom apartment for a family of 4...",
  "budget_min": 100.00,
  "budget_max": 200.00,
  "location": "Algiers",
  "points_cost": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": 1,
    "title": "Looking for 2-bedroom apartment in Algiers",
    "description": "I need a 2-bedroom apartment for a family of 4...",
    "budget_min": 100.00,
    "budget_max": 200.00,
    "location": "Algiers",
    "points_cost": 10,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### List Posts

**GET** `/api/v1/posts`

Get list of client posts.

**Query Parameters:**
- `page` (integer): Page number
- `size` (integer): Items per page
- `location` (string): Location filter
- `budget_min` (number): Minimum budget
- `budget_max` (number): Maximum budget

**Response:**
```json
{
  "success": true,
  "message": "Posts retrieved successfully",
  "data": {
    "posts": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "first_name": "John",
          "last_name": "Doe",
          "rating": 4.5
        },
        "title": "Looking for 2-bedroom apartment in Algiers",
        "description": "I need a 2-bedroom apartment for a family of 4...",
        "budget_min": 100.00,
        "budget_max": 200.00,
        "location": "Algiers",
        "points_cost": 10,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 25,
      "pages": 2,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Contact Post Creator

**POST** `/api/v1/posts/{post_id}/contact`

Contact the creator of a post.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "I have a property that matches your requirements..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `AUTH_INVALID_CREDENTIALS` | Invalid email or password |
| `AUTH_TOKEN_EXPIRED` | JWT token has expired |
| `AUTH_INVALID_TOKEN` | Invalid JWT token |
| `AUTH_INSUFFICIENT_PERMISSIONS` | User doesn't have required permissions |
| `USER_EMAIL_EXISTS` | Email address already registered |
| `USER_PHONE_EXISTS` | Phone number already registered |
| `USER_NOT_FOUND` | User not found |
| `PROPERTY_NOT_FOUND` | Property not found |
| `PROPERTY_NOT_AVAILABLE` | Property not available for requested dates |
| `BOOKING_NOT_FOUND` | Booking not found |
| `BOOKING_CANNOT_CANCEL` | Booking cannot be cancelled |
| `POST_NOT_FOUND` | Post not found |
| `INSUFFICIENT_POINTS` | User doesn't have enough points |
| `VALIDATION_ERROR` | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per 5 minutes
- **General endpoints**: 100 requests per minute per user
- **File uploads**: 10 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

---

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events

- `booking.created` - New booking created
- `booking.confirmed` - Booking confirmed by host
- `booking.cancelled` - Booking cancelled
- `payment.succeeded` - Payment completed
- `payment.failed` - Payment failed
- `review.created` - New review posted

### Webhook Configuration

To receive webhooks, register your endpoint:

**POST** `/api/v1/webhooks/register`

```json
{
  "url": "https://your-domain.com/webhooks",
  "events": ["booking.created", "payment.succeeded"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

Webhooks include a signature for verification:

```
X-Kerya-Signature: sha256=abc123...
```

Example payload:
```json
{
  "event": "booking.created",
  "data": {
    "booking_id": 1,
    "property_id": 1,
    "user_id": 1,
    "total_price": 300.00
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## SDKs and Libraries

Official SDKs are available for popular programming languages:

- **JavaScript/TypeScript**: `npm install @kerya/sdk`
- **Python**: `pip install kerya-sdk`
- **PHP**: `composer require kerya/sdk`
- **Java**: Maven dependency available
- **Swift**: iOS SDK available via CocoaPods

For more information and examples, visit our [SDK Documentation](https://docs.kerya.com/sdks). 
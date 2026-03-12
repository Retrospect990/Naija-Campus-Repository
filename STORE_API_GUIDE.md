# Campus Pinduoduo: Online Store API Documentation

## Overview

The Online Store API enables moderators to browse products, manage shopping carts with budget constraints, and place orders. This API integrates with the escrow system to enforce pool budget limits.

**Base URL:** `http://localhost:5000`

**Content-Type:** `application/json`

---

## Key Concepts

### Budget-Aware Shopping Cart
- Each cart is tied to a **pool** and has a maximum **pool_budget** (e.g., ₦50,000)
- Items cannot be added if they exceed the remaining budget
- API returns clear error messages showing budget shortfall
- Budget serves as the group's spending limit

### Order Lifecycle
```
PENDING → CONFIRMED → PAID → PROCESSING → SHIPPED → DELIVERED
                                        ↓
                                    CANCELLED
```

### Product Structure
Products can have **multiple brands** for the same category at different prices:
- **Rice** (Food category):
  - Uncle Ben's ₦25,000/bag
  - Golden Harvest ₦22,000/bag
- Moderators choose based on their pool budget

---

## Product Browsing Endpoints

### 1. List All Products
```http
GET /api/store/products
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Filter by category (food, beverages, fashion, etc) |
| `search` | string | No | Search by product name or brand |
| `brand` | string | No | Filter by brand name |
| `min_price` | float | No | Minimum price filter |
| `max_price` | float | No | Maximum price filter |
| `sort` | string | No | Sort by: `price_asc`, `price_desc`, `rating`, `newest` |
| `limit` | int | No | Results per page (default: 20) |
| `offset` | int | No | Pagination offset (default: 0) |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/products?category=food&sort=price_asc"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "name": "Rice",
      "brand": "Uncle Ben's",
      "category": "food",
      "price": 25000.00,
      "unit": "bag",
      "quantity_available": 100,
      "average_rating": 4.5,
      "supplier": "Northern Supplies",
      "description": "Premium long-grain rice"
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "limit": 20
  }
}
```

---

### 2. Get Single Product Details
```http
GET /api/store/products/{product_id}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/products/550e8400-e29b-41d4-a716-446655440000"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Rice",
    "brand": "Uncle Ben's",
    "price": 25000.00,
    "unit": "bag",
    "quantity_available": 100,
    "average_rating": 4.5,
    "rating_count": 23,
    "supplier": "Northern Supplies",
    "supplier_phone": "+234 700 123 4567",
    "category": "food",
    "description": "Premium long-grain rice, 100% natural",
    "reviews": [
      {
        "rating": 5,
        "text": "Excellent quality",
        "moderator": "Alice O.",
        "date": "2024-01-15"
      }
    ]
  }
}
```

---

### 3. List All Categories
```http
GET /api/store/categories
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/categories"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "name": "Food",
      "product_count": 12,
      "description": "Staples and bulk food items"
    },
    {
      "name": "Beverages",
      "product_count": 8,
      "description": "Drinks and beverages"
    }
  ]
}
```

---

### 4. Get Available Brands
```http
GET /api/store/brands
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter brands by category |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/brands?category=food"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "brand": "Uncle Ben's",
      "product_count": 3,
      "avg_price": 25000.00
    },
    {
      "brand": "Golden Harvest",
      "product_count": 2,
      "avg_price": 22000.00
    }
  ]
}
```

---

### 5. Search Products
```http
GET /api/store/search
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search term (min 2 characters) |
| `category` | string | No | Limit search to category |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/search?q=rice&category=food"
```

**Success Response (200):**
```json
{
  "status": "success",
  "results": [
    {
      "id": "uuid",
      "name": "Rice",
      "brand": "Uncle Ben's",
      "price": 25000.00,
      "match_score": 0.95
    }
  ],
  "total": 3
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Search term must be at least 2 characters"
}
```

---

## Shopping Cart Endpoints

### 6. Create Shopping Cart
```http
POST /api/cart/create
```

**Request Body:**
```json
{
  "moderator_id": "mod_001",
  "pool_id": "pool_rice_50000",
  "pool_budget": 50000.00
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/cart/create" \
  -H "Content-Type: application/json" \
  -d '{
    "moderator_id": "mod_tunde_001",
    "pool_id": "pool_rice_50000",
    "pool_budget": 50000.00
  }'
```

**Success Response (201):**
```json
{
  "status": "success",
  "message": "Cart created successfully",
  "data": {
    "cart_id": "cart_uuid",
    "moderator_id": "mod_tunde_001",
    "pool_id": "pool_rice_50000",
    "pool_budget": 50000.00,
    "items": [],
    "cart_total": 0.00,
    "remaining_budget": 50000.00,
    "budget_used_percent": 0.0,
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

---

### 7. View Shopping Cart
```http
GET /api/cart/{cart_id}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/cart/cart_uuid"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "cart_id": "cart_uuid",
    "moderator_id": "mod_tunde_001",
    "pool_budget": 50000.00,
    "items": [
      {
        "product_id": "prod_rice_001",
        "name": "Rice",
        "brand": "Uncle Ben's",
        "quantity": 1,
        "unit_price": 25000.00,
        "subtotal": 25000.00
      }
    ],
    "cart_total": 25000.00,
    "remaining_budget": 25000.00,
    "budget_used_percent": 50.0,
    "item_count": 1
  }
}
```

---

### 8. Add Item to Cart
```http
POST /api/cart/{cart_id}/add
```

**Request Body:**
```json
{
  "product_id": "prod_rice_001",
  "quantity": 1
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/cart/cart_uuid/add" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_rice_001",
    "quantity": 1
  }'
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Item added to cart",
  "data": {
    "cart_id": "cart_uuid",
    "item_added": {
      "product_id": "prod_rice_001",
      "name": "Rice",
      "quantity": 1,
      "unit_price": 25000.00
    },
    "cart_total": 25000.00,
    "remaining_budget": 25000.00,
    "budget_used_percent": 50.0
  }
}
```

**Error Response - Budget Exceeded (400):**
```json
{
  "status": "error",
  "message": "Insufficient budget. Need ₦25,000.00 but only ₦20,000.00 remaining. Cannot add 1x Rice."
}
```

**Error Response - Product Not Found (404):**
```json
{
  "status": "error",
  "message": "Product not found"
}
```

**Error Response - Insufficient Stock (400):**
```json
{
  "status": "error",
  "message": "Insufficient stock. Only 5 units available, requested 10"
}
```

---

### 9. Update Cart Item Quantity
```http
PUT /api/cart/{cart_id}/update/{product_id}
```

**Request Body:**
```json
{
  "quantity": 2
}
```

**Example Request:**
```bash
curl -X PUT "http://localhost:5000/api/cart/cart_uuid/update/prod_rice_001" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Quantity updated",
  "data": {
    "product_id": "prod_rice_001",
    "new_quantity": 2,
    "subtotal": 50000.00,
    "cart_total": 50000.00,
    "remaining_budget": 0.00,
    "budget_used_percent": 100.0
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Budget exceeded. Current usage: ₦25,000. Adding 2 units would cost ₦50,000 total, exceeds ₦30,000 budget."
}
```

---

### 10. Remove Item from Cart
```http
DELETE /api/cart/{cart_id}/remove/{product_id}
```

**Example Request:**
```bash
curl -X DELETE "http://localhost:5000/api/cart/cart_uuid/remove/prod_rice_001"
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Item removed from cart",
  "data": {
    "product_id": "prod_rice_001",
    "cart_total": 0.00,
    "remaining_budget": 50000.00,
    "item_count": 0
  }
}
```

---

### 11. Clear Entire Cart
```http
POST /api/cart/{cart_id}/clear
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/cart/cart_uuid/clear"
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Cart cleared",
  "data": {
    "cart_id": "cart_uuid",
    "item_count": 0,
    "cart_total": 0.00,
    "remaining_budget": 50000.00
  }
}
```

---

## Order Management Endpoints

### 12. Place Order (Convert Cart to Order)
```http
POST /api/orders/place
```

**Request Body:**
```json
{
  "cart_id": "cart_uuid",
  "notes": "Deliver to dormitory building A, room 204",
  "delivery_address": "Lagos State University, Student Housing"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/orders/place" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "cart_uuid",
    "notes": "Deliver to dormitory",
    "delivery_address": "LASU, Building A"
  }'
```

**Success Response (201):**
```json
{
  "status": "success",
  "message": "Order placed successfully",
  "data": {
    "order_id": "order_uuid",
    "order_number": "ORD-2024-00001",
    "status": "PENDING",
    "moderator_id": "mod_tunde_001",
    "pool_id": "pool_rice_50000",
    "items": [
      {
        "product_id": "prod_rice_001",
        "name": "Rice",
        "quantity": 1,
        "unit_price": 25000.00,
        "line_total": 25000.00
      }
    ],
    "total_amount": 25000.00,
    "notes": "Deliver to dormitory",
    "delivery_address": "LASU, Building A",
    "created_at": "2024-01-20T10:35:00Z"
  }
}
```

**Error Response - Empty Cart (400):**
```json
{
  "status": "error",
  "message": "Cannot place order: cart is empty"
}
```

---

### 13. Get Order Details
```http
GET /api/orders/{order_id}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/orders/order_uuid"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "order_id": "order_uuid",
    "order_number": "ORD-2024-00001",
    "status": "PENDING",
    "pool_id": "pool_rice_50000",
    "moderator_id": "mod_tunde_001",
    "items": [
      {
        "product_id": "prod_rice_001",
        "name": "Rice",
        "brand": "Uncle Ben's",
        "quantity": 1,
        "unit_price": 25000.00,
        "line_total": 25000.00
      },
      {
        "product_id": "prod_beans_001",
        "name": "Beans",
        "brand": "Local Premium",
        "quantity": 1,
        "unit_price": 12000.00,
        "line_total": 12000.00
      }
    ],
    "total_amount": 37000.00,
    "notes": "Deliver to dormitory",
    "delivery_address": "LASU, Building A",
    "expected_delivery_date": "2024-01-22",
    "created_at": "2024-01-20T10:35:00Z",
    "status_history": [
      {
        "status": "PENDING",
        "timestamp": "2024-01-20T10:35:00Z"
      }
    ]
  }
}
```

---

### 14. Get Moderator's Order History
```http
GET /api/orders/moderator/{moderator_id}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (PENDING, CONFIRMED, DELIVERED, etc) |
| `limit` | int | Number of orders to return (default: 20) |
| `offset` | int | Pagination offset (default: 0) |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/orders/moderator/mod_tunde_001?status=DELIVERED&limit=10"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "order_id": "order_uuid",
      "order_number": "ORD-2024-00001",
      "status": "DELIVERED",
      "total_amount": 37000.00,
      "item_count": 2,
      "created_at": "2024-01-20T10:35:00Z",
      "delivered_at": "2024-01-22T14:20:00Z"
    },
    {
      "order_id": "order_uuid_2",
      "order_number": "ORD-2024-00002",
      "status": "PENDING",
      "total_amount": 50000.00,
      "item_count": 1,
      "created_at": "2024-01-20T15:00:00Z"
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "limit": 10
  }
}
```

---

### 15. Update Order Status (Admin)
```http
PUT /api/orders/{order_id}/status
```

**Request Body:**
```json
{
  "new_status": "CONFIRMED",
  "reason": "Payment received"
}
```

**Valid Status Transitions:**
- PENDING → CONFIRMED (order verified)
- CONFIRMED → PAID (payment processed)
- PAID → PROCESSING (order being prepared)
- PROCESSING → SHIPPED (out for delivery)
- SHIPPED → DELIVERED (customer received)
- Any status → CANCELLED (if needed)

**Example Request:**
```bash
curl -X PUT "http://localhost:5000/api/orders/order_uuid/status" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "CONFIRMED",
    "reason": "Payment verified"
  }'
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Order status updated",
  "data": {
    "order_id": "order_uuid",
    "old_status": "PENDING",
    "new_status": "CONFIRMED",
    "updated_at": "2024-01-20T11:00:00Z"
  }
}
```

---

## Analytics & System Endpoints

### 16. Get Store Statistics
```http
GET /api/store/stats
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/stats"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_products": 45,
    "product_categories": 8,
    "stock_value": 2500000.00,
    "active_carts": 12,
    "total_orders": 87,
    "total_sales": 1250000.00,
    "top_products": [
      {
        "name": "Rice",
        "total_sold_qty": 45,
        "total_revenue": 1125000.00
      }
    ],
    "recent_orders": [
      {
        "order_id": "order_uuid",
        "total": 50000.00,
        "created_at": "2024-01-20T10:35:00Z"
      }
    ]
  }
}
```

---

### 17. Check Inventory Status
```http
GET /api/store/inventory
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: low_stock, out_of_stock, ok |

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/inventory?status=low_stock"
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "products": [
      {
        "product_id": "prod_usb_001",
        "name": "USB Cable",
        "brand": "Generic",
        "quantity_available": 3,
        "reorder_level": 10,
        "status": "LOW_STOCK",
        "action_required": "Reorder immediately"
      }
    ],
    "summary": {
      "ok_count": 38,
      "low_stock_count": 5,
      "out_of_stock_count": 2
    }
  }
}
```

---

### 18. Service Health Check
```http
GET /api/store/health
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/store/health"
```

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:40:00Z",
  "database": "connected",
  "products_loaded": 45,
  "version": "1.0.0"
}
```

---

## Error Handling

All error responses follow this format:

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_REQUEST | 400 | Malformed request |
| CART_NOT_FOUND | 404 | Cart doesn't exist |
| PRODUCT_NOT_FOUND | 404 | Product not found |
| INSUFFICIENT_BUDGET | 400 | Item exceeds remaining budget |
| INSUFFICIENT_STOCK | 400 | Not enough items in stock |
| EMPTY_CART | 400 | Cannot place order with empty cart |
| ORDER_NOT_FOUND | 404 | Order not found |
| INVALID_STATUS_TRANSITION | 400 | Invalid order status change |
| UNAUTHORIZED | 401 | Not authenticated |
| FORBIDDEN | 403 | Not authorized for this action |
| SERVER_ERROR | 500 | Internal server error |

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **Product browsing**: 100 requests per minute
- **Cart operations**: 50 requests per minute
- **Order operations**: 30 requests per minute

Response includes rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705761600
```

---

## Authentication

All endpoints except product browsing (`GET /api/store/products`, etc) require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

---

## Integration with Escrow System

When an order is placed:
1. Order amount is **deducted from pool budget**
2. Order is linked to the pool (`pool_id`)
3. Inventory is updated
4. Escrow system can be triggered for fund release upon delivery confirmation

---

## Best Practices

### For Moderators
1. **Browse first**: Use `/api/store/products` and `/api/store/search` to find items
2. **Check budget**: Always review `remaining_budget` before adding items
3. **Modify carefully**: Update quantities with `/api/cart/{id}/update/{product_id}`
4. **Confirm orders**: Review cart total before calling `/api/orders/place`
5. **Track orders**: Use `/api/orders/moderator/{id}` to check delivery status

### For Developers
1. **Validate locally**: Check remaining budget before API calls (better UX)
2. **Handle budget errors**: Show users the exact shortfall
3. **Retry logic**: Implement exponential backoff for transient errors
4. **Cache products**: Products rarely change; cache for 1 hour
5. **Handle 404s**: Gracefully handle product_not_found errors

---

## Example Workflow

```bash
# 1. Browse products
curl -X GET "http://localhost:5000/api/store/products?category=food"

# 2. Create cart with ₦50,000 budget
curl -X POST "http://localhost:5000/api/cart/create" \
  -H "Content-Type: application/json" \
  -d '{
    "moderator_id": "mod_001",
    "pool_id": "pool_001",
    "pool_budget": 50000
  }'
# Response includes cart_id

# 3. Add rice to cart
curl -X POST "http://localhost:5000/api/cart/{cart_id}/add" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod_rice_001", "quantity": 1}'

# 4. Add beans to cart
curl -X POST "http://localhost:5000/api/cart/{cart_id}/add" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod_beans_001", "quantity": 1}'

# 5. View cart
curl -X GET "http://localhost:5000/api/cart/{cart_id}"

# 6. Place order
curl -X POST "http://localhost:5000/api/orders/place" \
  -H "Content-Type: application/json" \
  -d '{"cart_id": "{cart_id}"}'

# 7. Check order status
curl -X GET "http://localhost:5000/api/orders/{order_id}"

# 8. View order history
curl -X GET "http://localhost:5000/api/orders/moderator/mod_001"
```

---

## Webhooks & Events

The system can emit webhook events for integrations:

- `order.created`: Order placed
- `order.confirmed`: Order confirmed
- `order.shipped`: Order shipped
- `order.delivered`: Order delivered
- `inventory.low_stock`: Low stock alert
- `cart.abandoned`: Cart not converted to order after 24 hours

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-20 | Initial release |

---

## Support & Questions

For API support or questions:
- **Email:** support@campuspinduoduo.local
- **Slack:** #store-api-support
- **Documentation:** https://docs.campuspinduoduo.local/store-api

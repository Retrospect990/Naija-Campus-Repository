package com.campuspinduoduo.model

import java.util.Date

enum class OrderStatus {
    PENDING,
    CONFIRMED,
    PAID,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED
}

data class Order(
    val orderId: String,
    val poolId: String,
    val items: List<CartItem>,
    val totalAmount: Double,
    val status: OrderStatus,
    val createdAt: Long,
    val updatedAt: Long,
    val estimatedDelivery: Long? = null,
    val trackingNumber: String = "",
    val moderatorId: String = "",
    val poolBudget: Double = 0.0
)

data class PlaceOrderRequest(
    val poolId: String,
    val items: List<CartItem>,
    val totalAmount: Double,
    val moderatorId: String
)

data class PlaceOrderResponse(
    val status: String,
    val message: String,
    val order: Order?
)

data class OrderTrackingResponse(
    val status: String,
    val order: Order?
)

data class UserOrdersResponse(
    val status: String,
    val orders: List<Order>
)

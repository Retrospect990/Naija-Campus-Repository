package com.campuspinduoduo.model

data class CartItem(
    val productId: String,
    val productName: String,
    val price: Double,
    val quantity: Int,
    val imageUrl: String = "",
    val supplier: String = ""
)

data class Cart(
    val poolId: String,
    val items: List<CartItem> = emptyList(),
    val poolBudget: Double,
    val totalPrice: Double = 0.0
) {
    fun remainingBudget(): Double = poolBudget - totalPrice
    fun canAddItem(itemPrice: Double): Boolean = (totalPrice + itemPrice) <= poolBudget
}

data class AddToCartRequest(
    val productId: String,
    val quantity: Int
)

data class AddToCartResponse(
    val status: String,
    val message: String,
    val cart: Cart?
)

data class RemoveFromCartRequest(
    val productId: String
)

data class UpdateCartResponse(
    val status: String,
    val cart: Cart?
)

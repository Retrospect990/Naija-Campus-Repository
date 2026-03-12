package com.campuspinduoduo.api

import retrofit2.Call
import retrofit2.http.*
import com.campuspinduoduo.model.*

interface StoreApiService {

    // ==================== PRODUCT ENDPOINTS ====================
    
    @GET("/api/store/products")
    fun getAllProducts(
        @Query("category") category: String? = null,
        @Query("search") search: String? = null,
        @Query("brand") brand: String? = null,
        @Query("min_price") minPrice: Double? = null,
        @Query("max_price") maxPrice: Double? = null
    ): Call<ProductResponse>

    @GET("/api/store/products/{product_id}")
    fun getProductDetails(
        @Path("product_id") productId: String
    ): Call<ProductDetailResponse>

    @GET("/api/store/categories")
    fun getCategories(): Call<Map<String, Any>>

    // ==================== CART ENDPOINTS ====================

    @POST("/api/store/cart/{pool_id}/add")
    fun addToCart(
        @Path("pool_id") poolId: String,
        @Body request: AddToCartRequest
    ): Call<AddToCartResponse>

    @POST("/api/store/cart/{pool_id}/remove")
    fun removeFromCart(
        @Path("pool_id") poolId: String,
        @Body request: RemoveFromCartRequest
    ): Call<UpdateCartResponse>

    @GET("/api/store/cart/{pool_id}")
    fun getCart(
        @Path("pool_id") poolId: String
    ): Call<Cart>

    @POST("/api/store/cart/{pool_id}/clear")
    fun clearCart(
        @Path("pool_id") poolId: String
    ): Call<UpdateCartResponse>

    // ==================== ORDER ENDPOINTS ====================

    @POST("/api/store/orders/place")
    fun placeOrder(
        @Body request: PlaceOrderRequest
    ): Call<PlaceOrderResponse>

    @GET("/api/store/orders/{order_id}")
    fun getOrderDetails(
        @Path("order_id") orderId: String
    ): Call<OrderTrackingResponse>

    @GET("/api/store/orders/user/{user_id}")
    fun getUserOrders(
        @Path("user_id") userId: String
    ): Call<UserOrdersResponse>

    @GET("/api/store/orders/pool/{pool_id}")
    fun getPoolOrders(
        @Path("pool_id") poolId: String
    ): Call<UserOrdersResponse>

    // ==================== POOL ENDPOINTS ====================

    @GET("/api/pools")
    fun getPools(): Call<PoolsResponse>

    @GET("/api/pools/{pool_id}")
    fun getPoolDetails(
        @Path("pool_id") poolId: String
    ): Call<PoolDetailResponse>

    @POST("/api/pools/{pool_id}/join")
    fun joinPool(
        @Path("pool_id") poolId: String,
        @Body request: JoinPoolRequest
    ): Call<JoinPoolResponse>

    // ==================== DELIVERY CONFIRMATION ====================

    @POST("/api/store/delivery/{order_id}/confirm")
    fun confirmDelivery(
        @Path("order_id") orderId: String,
        @Body request: Map<String, String>
    ): Call<Map<String, Any>>

    // ==================== STATS & INFO ====================

    @GET("/api/stats")
    fun getStats(): Call<Map<String, Any>>

    @GET("/api/health")
    fun healthCheck(): Call<Map<String, Any>>
}

package com.campuspinduoduo.model

data class User(
    val userId: String,
    val name: String,
    val email: String,
    val phone: String = "",
    val profileImage: String = "",
    val createdAt: Long = 0,
    val isModerator: Boolean = false,
    val totalOrders: Int = 0,
    val totalSpent: Double = 0.0,
    val rating: Double = 0.0
)

data class UserResponse(
    val status: String,
    val user: User?
)

data class AuthRequest(
    val email: String,
    val password: String
)

data class AuthResponse(
    val status: String,
    val token: String?,
    val user: User?,
    val message: String?
)

data class UpdateProfileRequest(
    val name: String,
    val phone: String,
    val profileImage: String?
)

data class UpdateProfileResponse(
    val status: String,
    val user: User?
)

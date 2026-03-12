package com.campuspinduoduo.model

enum class PoolStatus {
    ACTIVE,
    LOCKED,
    IN_DELIVERY,
    COMPLETED,
    CANCELLED
}

data class Pool(
    val poolId: String,
    val poolName: String,
    val moderatorId: String,
    val goal: Double,
    val currentAmount: Double,
    val status: PoolStatus,
    val members: Int,
    val createdAt: Long,
    val deadline: Long?,
    val description: String = ""
)

data class JoinPoolRequest(
    val userId: String,
    val amount: Double
)

data class JoinPoolResponse(
    val status: String,
    val message: String,
    val pool: Pool?
)

data class PoolsResponse(
    val status: String,
    val pools: List<Pool>
)

data class PoolDetailResponse(
    val status: String,
    val pool: Pool?
)

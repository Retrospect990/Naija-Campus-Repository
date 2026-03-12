package com.campuspinduoduo.model

data class Product(
    val id: String,
    val name: String,
    val brand: String,
    val category: String,
    val price: Double,
    val description: String,
    val available: Int,
    val unit: String,
    val rating: Double,
    val reviews: Int,
    val supplier: String,
    val imageUrl: String = ""
)

data class ProductResponse(
    val status: String,
    val count: Int,
    val products: List<Product>
)

data class ProductDetailResponse(
    val status: String,
    val product: Product
)

data class Category(
    val name: String,
    val displayName: String,
    val count: Int
)

data class CategoriesResponse(
    val status: String,
    val categories: List<Category>
)

package com.campuspinduoduo.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.LiveData
import android.app.Application
import com.campuspinduoduo.api.RetrofitClient
import com.campuspinduoduo.model.CartItem
import com.campuspinduoduo.model.Cart
import com.campuspinduoduo.model.AddToCartRequest
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class CartViewModel(private val application: Application) : ViewModel() {

    private val apiService = RetrofitClient.getApiService()

    private val _cartItems = MutableLiveData<List<CartItem>>(emptyList())
    val cartItems: LiveData<List<CartItem>> = _cartItems

    private val _cart = MutableLiveData<Cart>()
    val cart: LiveData<Cart> = _cart

    private val _totalPrice = MutableLiveData<Double>(0.0)
    val totalPrice: LiveData<Double> = _totalPrice

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    private var currentPoolId: String = ""

    fun setPoolId(poolId: String) {
        currentPoolId = poolId
        loadCart()
    }

    fun loadCart() {
        if (currentPoolId.isEmpty()) return

        _isLoading.value = true
        apiService.getCart(currentPoolId).enqueue(object : Callback<Cart> {
            override fun onResponse(call: Call<Cart>, response: Response<Cart>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    response.body()?.let {
                        _cart.value = it
                        _cartItems.value = it.items
                        _totalPrice.value = it.totalPrice
                    }
                }
            }

            override fun onFailure(call: Call<Cart>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Failed to load cart"
            }
        })
    }

    fun addToCart(productId: String, quantity: Int) {
        if (currentPoolId.isEmpty()) {
            _error.value = "No pool selected"
            return
        }

        _isLoading.value = true
        val request = AddToCartRequest(productId, quantity)
        apiService.addToCart(currentPoolId, request).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    loadCart()
                } else {
                    _error.value = "Failed to add item to cart"
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Error adding to cart"
            }
        })
    }

    fun removeFromCart(productId: String) {
        if (currentPoolId.isEmpty()) return

        _isLoading.value = true
        val request = mapOf("productId" to productId)
        apiService.removeFromCart(currentPoolId, com.campuspinduoduo.model.RemoveFromCartRequest(productId))
            .enqueue(object : Callback<Any> {
                override fun onResponse(call: Call<Any>, response: Response<Any>) {
                    _isLoading.value = false
                    if (response.isSuccessful) {
                        loadCart()
                    }
                }

                override fun onFailure(call: Call<Any>, t: Throwable) {
                    _isLoading.value = false
                    _error.value = t.message
                }
            })
    }

    fun clearCart() {
        if (currentPoolId.isEmpty()) return

        _isLoading.value = true
        apiService.clearCart(currentPoolId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    _cartItems.value = emptyList()
                    _totalPrice.value = 0.0
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun getRemainingBudget(): Double {
        return _cart.value?.remainingBudget() ?: 0.0
    }

    fun canAddItem(itemPrice: Double): Boolean {
        return _cart.value?.canAddItem(itemPrice) ?: false
    }
}

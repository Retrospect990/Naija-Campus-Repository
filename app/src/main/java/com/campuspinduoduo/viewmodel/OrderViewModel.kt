package com.campuspinduoduo.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.LiveData
import android.app.Application
import com.campuspinduoduo.api.RetrofitClient
import com.campuspinduoduo.model.Order
import com.campuspinduoduo.model.PlaceOrderRequest
import com.campuspinduoduo.model.CartItem
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class OrderViewModel(private val application: Application) : ViewModel() {

    private val apiService = RetrofitClient.getApiService()

    private val _orders = MutableLiveData<List<Order>>()
    val orders: LiveData<List<Order>> = _orders

    private val _selectedOrder = MutableLiveData<Order>()
    val selectedOrder: LiveData<Order> = _selectedOrder

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _orderPlaced = MutableLiveData<Boolean>()
    val orderPlaced: LiveData<Boolean> = _orderPlaced

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun getUserOrders(userId: String) {
        _isLoading.value = true
        apiService.getUserOrders(userId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    // Parse orders from response
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun getPoolOrders(poolId: String) {
        _isLoading.value = true
        apiService.getPoolOrders(poolId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    // Parse orders from response
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun getOrderDetails(orderId: String) {
        _isLoading.value = true
        apiService.getOrderDetails(orderId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                // Parse order from response
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun placeOrder(
        poolId: String,
        items: List<CartItem>,
        totalAmount: Double,
        moderatorId: String
    ) {
        _isLoading.value = true
        val request = PlaceOrderRequest(poolId, items, totalAmount, moderatorId)
        
        apiService.placeOrder(request).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    _orderPlaced.value = true
                } else {
                    _error.value = "Failed to place order"
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun confirmDelivery(orderId: String, pinCode: String) {
        _isLoading.value = true
        apiService.confirmDelivery(orderId, mapOf("pin_code" to pinCode))
            .enqueue(object : Callback<Map<String, Any>> {
                override fun onResponse(
                    call: Call<Map<String, Any>>,
                    response: Response<Map<String, Any>>
                ) {
                    _isLoading.value = false
                    if (response.isSuccessful) {
                        getOrderDetails(orderId)
                    }
                }

                override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                    _isLoading.value = false
                    _error.value = t.message
                }
            })
    }
}

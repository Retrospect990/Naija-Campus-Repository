package com.campuspinduoduo.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.LiveData
import android.app.Application
import com.campuspinduoduo.api.RetrofitClient
import com.campuspinduoduo.model.Product
import com.campuspinduoduo.model.ProductResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ProductViewModel(private val application: Application) : ViewModel() {

    private val apiService = RetrofitClient.getApiService()

    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _selectedProduct = MutableLiveData<Product>()
    val selectedProduct: LiveData<Product> = _selectedProduct

    private val _categories = MutableLiveData<List<String>>()
    val categories: LiveData<List<String>> = _categories

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun getAllProducts() {
        _isLoading.value = true
        apiService.getAllProducts().enqueue(object : Callback<ProductResponse> {
            override fun onResponse(call: Call<ProductResponse>, response: Response<ProductResponse>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    response.body()?.let {
                        _products.value = it.products
                    }
                } else {
                    _error.value = "Failed to load products"
                }
            }

            override fun onFailure(call: Call<ProductResponse>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Unknown error occurred"
            }
        })
    }

    fun searchProducts(query: String) {
        _isLoading.value = true
        apiService.getAllProducts(search = query).enqueue(object : Callback<ProductResponse> {
            override fun onResponse(call: Call<ProductResponse>, response: Response<ProductResponse>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    _products.value = response.body()?.products ?: emptyList()
                }
            }

            override fun onFailure(call: Call<ProductResponse>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Search failed"
            }
        })
    }

    fun filterByCategory(category: String) {
        _isLoading.value = true
        apiService.getAllProducts(category = category).enqueue(object : Callback<ProductResponse> {
            override fun onResponse(call: Call<ProductResponse>, response: Response<ProductResponse>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    _products.value = response.body()?.products ?: emptyList()
                }
            }

            override fun onFailure(call: Call<ProductResponse>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Filter failed"
            }
        })
    }

    fun getProductDetails(productId: String) {
        _isLoading.value = true
        apiService.getProductDetails(productId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    // Parse manually since response structure contains nested product
                    _selectedProduct.value = _selectedProduct.value
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message ?: "Failed to load product details"
            }
        })
    }

    fun getCategories() {
        apiService.getCategories().enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                // Parse categories from response
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _error.value = "Failed to load categories"
            }
        })
    }
}

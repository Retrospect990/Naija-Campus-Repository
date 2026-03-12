package com.campuspinduoduo.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.LiveData
import android.app.Application
import com.campuspinduoduo.api.RetrofitClient
import com.campuspinduoduo.model.Pool
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class PoolViewModel(private val application: Application) : ViewModel() {

    private val apiService = RetrofitClient.getApiService()

    private val _pools = MutableLiveData<List<Pool>>()
    val pools: LiveData<List<Pool>> = _pools

    private val _selectedPool = MutableLiveData<Pool>()
    val selectedPool: LiveData<Pool> = _selectedPool

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun getPools() {
        _isLoading.value = true
        apiService.getPools().enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    // Parse pools from response
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun getPoolDetails(poolId: String) {
        _isLoading.value = true
        apiService.getPoolDetails(poolId).enqueue(object : Callback<Any> {
            override fun onResponse(call: Call<Any>, response: Response<Any>) {
                _isLoading.value = false
                if (response.isSuccessful) {
                    // Parse pool details from response
                }
            }

            override fun onFailure(call: Call<Any>, t: Throwable) {
                _isLoading.value = false
                _error.value = t.message
            }
        })
    }

    fun joinPool(poolId: String, userId: String, amount: Double) {
        _isLoading.value = true
        val request = mapOf(
            "userId" to userId,
            "amount" to amount
        )
        apiService.joinPool(poolId, com.campuspinduoduo.model.JoinPoolRequest(userId, amount))
            .enqueue(object : Callback<Any> {
                override fun onResponse(call: Call<Any>, response: Response<Any>) {
                    _isLoading.value = false
                    if (response.isSuccessful) {
                        getPools()
                    }
                }

                override fun onFailure(call: Call<Any>, t: Throwable) {
                    _isLoading.value = false
                    _error.value = t.message
                }
            })
    }
}

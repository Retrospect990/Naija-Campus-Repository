package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.content.Intent
import com.campuspinduoduo.R
import com.campuspinduoduo.viewmodel.OrderViewModel
import com.campuspinduoduo.viewmodel.ViewModelFactory
import com.campuspinduoduo.ui.adapters.OrderAdapter

class OrderTrackingActivity : AppCompatActivity() {

    private lateinit var orderViewModel: OrderViewModel
    private lateinit var orderAdapter: OrderAdapter
    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order_tracking)

        initializeViews()
        initializeViewModel()
        setupRecyclerView()
        loadOrders()
    }

    private fun initializeViews() {
        recyclerView = findViewById(R.id.orders_recycler)
    }

    private fun initializeViewModel() {
        val factory = ViewModelFactory(application)
        orderViewModel = ViewModelProvider(this, factory).get(OrderViewModel::class.java)
    }

    private fun setupRecyclerView() {
        orderAdapter = OrderAdapter(emptyList()) { order ->
            // Navigate to order detail or show order tracking
            Toast.makeText(this, "Order: ${order.orderId} - Status: ${order.status}", Toast.LENGTH_SHORT).show()
        }

        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@OrderTrackingActivity)
            adapter = orderAdapter
        }
    }

    private fun loadOrders() {
        // Load user's orders - in production, get actual userId
        val userId = "current_user"
        orderViewModel.getUserOrders(userId)

        orderViewModel.orders.observe(this) { orders ->
            orderAdapter.updateOrders(orders)
        }

        orderViewModel.error.observe(this) { error ->
            Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
        }
    }
}

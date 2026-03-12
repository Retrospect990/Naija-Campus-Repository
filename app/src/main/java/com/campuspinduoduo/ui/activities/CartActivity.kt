package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.content.Intent
import com.campuspinduoduo.R
import com.campuspinduoduo.viewmodel.CartViewModel
import com.campuspinduoduo.viewmodel.ViewModelFactory
import com.campuspinduoduo.ui.adapters.CartAdapter

class CartActivity : AppCompatActivity() {

    private lateinit var cartViewModel: CartViewModel
    private lateinit var cartAdapter: CartAdapter
    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_cart)

        initializeViews()
        initializeViewModel()
        setupRecyclerView()
        loadCart()
    }

    private fun initializeViews() {
        recyclerView = findViewById(R.id.cart_recycler)
    }

    private fun initializeViewModel() {
        val factory = ViewModelFactory(application)
        cartViewModel = ViewModelProvider(this, factory).get(CartViewModel::class.java)
        cartViewModel.setPoolId("default_pool")
    }

    private fun setupRecyclerView() {
        cartAdapter = CartAdapter(emptyList()) { productId ->
            cartViewModel.removeFromCart(productId)
        }

        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@CartActivity)
            adapter = cartAdapter
        }
    }

    private fun loadCart() {
        cartViewModel.cartItems.observe(this) { items ->
            cartAdapter.updateItems(items)
        }

        cartViewModel.totalPrice.observe(this) { totalPrice ->
            findViewById<TextView>(R.id.cart_total_price).text = 
                "Total: ₦${String.format("%.2f", totalPrice)}"
        }

        cartViewModel.cart.observe(this) { cart ->
            val remaining = cart.remainingBudget()
            findViewById<TextView>(R.id.cart_remaining_budget).text = 
                "Remaining Budget: ₦${String.format("%.2f", remaining)}"
        }

        cartViewModel.error.observe(this) { error ->
            Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btn_checkout).setOnClickListener {
            startActivity(Intent(this, CheckoutActivity::class.java))
        }

        findViewById<Button>(R.id.btn_clear_cart).setOnClickListener {
            cartViewModel.clearCart()
            Toast.makeText(this, "Cart cleared", Toast.LENGTH_SHORT).show()
        }
    }
}

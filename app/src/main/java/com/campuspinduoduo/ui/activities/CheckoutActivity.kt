package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import com.campuspinduoduo.R
import com.campuspinduoduo.viewmodel.CartViewModel
import com.campuspinduoduo.viewmodel.OrderViewModel
import com.campuspinduoduo.viewmodel.ViewModelFactory

class CheckoutActivity : AppCompatActivity() {

    private lateinit var cartViewModel: CartViewModel
    private lateinit var orderViewModel: OrderViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_checkout)

        initializeViewModels()
        loadCheckoutSummary()
        setupCheckoutButton()
    }

    private fun initializeViewModels() {
        val factory = ViewModelFactory(application)
        cartViewModel = ViewModelProvider(this, factory).get(CartViewModel::class.java)
        orderViewModel = ViewModelProvider(this, factory).get(OrderViewModel::class.java)
        cartViewModel.setPoolId("default_pool")
    }

    private fun loadCheckoutSummary() {
        cartViewModel.cart.observe(this) { cart ->
            findViewById<TextView>(R.id.checkout_item_count).text = 
                "Items: ${cart.items.size}"
            findViewById<TextView>(R.id.checkout_total_amount).text = 
                "Total: ₦${String.format("%.2f", cart.totalPrice)}"
            findViewById<TextView>(R.id.checkout_budget_info).text = 
                "Pool Budget: ₦${String.format("%.2f", cart.poolBudget)}"
        }
    }

    private fun setupCheckoutButton() {
        findViewById<Button>(R.id.btn_confirm_checkout).setOnClickListener {
            val moderatorId = findViewById<EditText>(R.id.moderator_id_input).text.toString()
            
            if (moderatorId.isEmpty()) {
                Toast.makeText(this, "Please enter moderator ID", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            cartViewModel.cart.value?.let { cart ->
                orderViewModel.placeOrder(
                    poolId = "default_pool",
                    items = cart.items,
                    totalAmount = cart.totalPrice,
                    moderatorId = moderatorId
                )
            }

            orderViewModel.orderPlaced.observe(this) { placed ->
                if (placed) {
                    Toast.makeText(this, "Order placed successfully!", Toast.LENGTH_LONG).show()
                    finish()
                }
            }

            orderViewModel.error.observe(this) { error ->
                Toast.makeText(this, "Error: $error", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

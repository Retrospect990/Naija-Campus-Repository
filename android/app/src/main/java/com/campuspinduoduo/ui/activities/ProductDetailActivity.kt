package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import com.campuspinduoduo.R
import com.campuspinduoduo.viewmodel.ProductViewModel
import com.campuspinduoduo.viewmodel.CartViewModel
import com.campuspinduoduo.viewmodel.ViewModelFactory

class ProductDetailActivity : AppCompatActivity() {

    private lateinit var productViewModel: ProductViewModel
    private lateinit var cartViewModel: CartViewModel
    private var productId: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_detail)

        productId = intent.getStringExtra("product_id") ?: ""
        initializeViewModels()
        loadProductDetails()
        setupAddToCartButton()
    }

    private fun initializeViewModels() {
        val factory = ViewModelFactory(application)
        productViewModel = ViewModelProvider(this, factory).get(ProductViewModel::class.java)
        cartViewModel = ViewModelProvider(this, factory).get(CartViewModel::class.java)
    }

    private fun loadProductDetails() {
        productViewModel.getProductDetails(productId)

        productViewModel.selectedProduct.observe(this) { product ->
            findViewById<TextView>(R.id.detail_product_name).text = product.name
            findViewById<TextView>(R.id.detail_product_brand).text = "Brand: ${product.brand}"
            findViewById<TextView>(R.id.detail_product_price).text = "₦${String.format("%.2f", product.price)}"
            findViewById<TextView>(R.id.detail_product_category).text = "Category: ${product.category}"
            findViewById<TextView>(R.id.detail_product_description).text = product.description
            findViewById<TextView>(R.id.detail_product_rating).text = "Rating: ${product.rating}/5 (${product.reviews} reviews)"
            findViewById<TextView>(R.id.detail_product_available).text = "Available: ${product.available} units"
        }

        productViewModel.error.observe(this) { error ->
            Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupAddToCartButton() {
        findViewById<Button>(R.id.btn_add_to_cart).setOnClickListener {
            val quantity = findViewById<android.widget.EditText>(R.id.quantity_input).text.toString().toIntOrNull() ?: 1
            
            // For now, use a default pool ID - in production this would be selected by user
            val poolId = "default_pool"
            cartViewModel.setPoolId(poolId)
            cartViewModel.addToCart(productId, quantity)

            Toast.makeText(this, "Added to cart!", Toast.LENGTH_SHORT).show()
        }
    }
}

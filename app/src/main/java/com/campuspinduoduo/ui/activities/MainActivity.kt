package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.content.Intent
import com.campuspinduoduo.R
import com.campuspinduoduo.viewmodel.ProductViewModel
import com.campuspinduoduo.viewmodel.ViewModelFactory
import com.campuspinduoduo.ui.adapters.ProductAdapter

class MainActivity : AppCompatActivity() {

    private lateinit var productViewModel: ProductViewModel
    private lateinit var productAdapter: ProductAdapter
    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeViews()
        initializeViewModel()
        setupRecyclerView()
        loadProducts()
    }

    private fun initializeViews() {
        recyclerView = findViewById(R.id.products_recycler)
    }

    private fun initializeViewModel() {
        val factory = ViewModelFactory(application)
        productViewModel = ViewModelProvider(this, factory).get(ProductViewModel::class.java)
    }

    private fun setupRecyclerView() {
        productAdapter = ProductAdapter(emptyList()) { product ->
            val intent = Intent(this, ProductDetailActivity::class.java)
            intent.putExtra("product_id", product.id)
            startActivity(intent)
        }

        recyclerView.apply {
            layoutManager = GridLayoutManager(this@MainActivity, 2)
            adapter = productAdapter
        }
    }

    private fun loadProducts() {
        productViewModel.getAllProducts()

        productViewModel.products.observe(this) { products ->
            productAdapter.updateProducts(products)
        }

        productViewModel.isLoading.observe(this) { isLoading ->
            // Update loading state UI
        }

        productViewModel.error.observe(this) { error ->
            Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_cart -> {
                startActivity(Intent(this, CartActivity::class.java))
                true
            }
            R.id.action_orders -> {
                startActivity(Intent(this, OrderTrackingActivity::class.java))
                true
            }
            R.id.action_profile -> {
                startActivity(Intent(this, ProfileActivity::class.java))
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}

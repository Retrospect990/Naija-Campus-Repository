package com.campuspinduoduo.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import android.widget.ImageView
import android.widget.TextView
import com.campuspinduoduo.model.Product
import com.campuspinduoduo.R

class ProductAdapter(
    private var products: List<Product> = emptyList(),
    private val onProductClick: (Product) -> Unit
) : RecyclerView.Adapter<ProductAdapter.ProductViewHolder>() {

    class ProductViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        val productName: TextView = itemView.findViewById(R.id.product_name)
        val productBrand: TextView = itemView.findViewById(R.id.product_brand)
        val productPrice: TextView = itemView.findViewById(R.id.product_price)
        val productImage: ImageView = itemView.findViewById(R.id.product_image)
        val productRating: TextView = itemView.findViewById(R.id.product_rating)
        val productAvailable: TextView = itemView.findViewById(R.id.product_available)

        fun bind(product: Product, onProductClick: (Product) -> Unit) {
            productName.text = product.name
            productBrand.text = product.brand
            productPrice.text = "₦${String.format("%.2f", product.price)}"
            productRating.text = "⭐ ${product.rating}/5 (${product.reviews})"
            productAvailable.text = "${product.available} available"
            
            itemView.setOnClickListener { onProductClick(product) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_product, parent, false)
        return ProductViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: ProductViewHolder, position: Int) {
        holder.bind(products[position], onProductClick)
    }

    override fun getItemCount(): Int = products.size

    fun updateProducts(newProducts: List<Product>) {
        products = newProducts
        notifyDataSetChanged()
    }
}

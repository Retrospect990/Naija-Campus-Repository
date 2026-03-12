package com.campuspinduoduo.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import com.campuspinduoduo.model.CartItem
import com.campuspinduoduo.R

class CartAdapter(
    private var items: List<CartItem> = emptyList(),
    private val onRemoveClick: (String) -> Unit
) : RecyclerView.Adapter<CartAdapter.CartViewHolder>() {

    class CartViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        val itemName: TextView = itemView.findViewById(R.id.cart_item_name)
        val itemPrice: TextView = itemView.findViewById(R.id.cart_item_price)
        val itemQuantity: TextView = itemView.findViewById(R.id.cart_item_quantity)
        val itemSupplier: TextView = itemView.findViewById(R.id.cart_item_supplier)
        val removeButton: ImageButton = itemView.findViewById(R.id.btn_remove_item)

        fun bind(item: CartItem, onRemoveClick: (String) -> Unit) {
            itemName.text = item.productName
            itemPrice.text = "₦${String.format("%.2f", item.price * item.quantity)}"
            itemQuantity.text = "Qty: ${item.quantity}"
            itemSupplier.text = "Supplier: ${item.supplier}"
            removeButton.setOnClickListener { onRemoveClick(item.productId) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CartViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_cart, parent, false)
        return CartViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: CartViewHolder, position: Int) {
        holder.bind(items[position], onRemoveClick)
    }

    override fun getItemCount(): Int = items.size

    fun updateItems(newItems: List<CartItem>) {
        items = newItems
        notifyDataSetChanged()
    }
}

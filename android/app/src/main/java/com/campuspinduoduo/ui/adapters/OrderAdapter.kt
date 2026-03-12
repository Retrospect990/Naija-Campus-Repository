package com.campuspinduoduo.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import android.widget.TextView
import com.campuspinduoduo.model.Order
import com.campuspinduoduo.R
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class OrderAdapter(
    private var orders: List<Order> = emptyList(),
    private val onOrderClick: (Order) -> Unit
) : RecyclerView.Adapter<OrderAdapter.OrderViewHolder>() {

    class OrderViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        val orderId: TextView = itemView.findViewById(R.id.order_id)
        val orderStatus: TextView = itemView.findViewById(R.id.order_status)
        val orderAmount: TextView = itemView.findViewById(R.id.order_amount)
        val orderDate: TextView = itemView.findViewById(R.id.order_date)
        val orderItemCount: TextView = itemView.findViewById(R.id.order_item_count)

        fun bind(order: Order, onOrderClick: (Order) -> Unit) {
            orderId.text = "Order #${order.orderId}"
            orderStatus.text = "Status: ${order.status.name}"
            orderAmount.text = "₦${String.format("%.2f", order.totalAmount)}"
            
            val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
            orderDate.text = "Date: ${dateFormat.format(Date(order.createdAt))}"
            orderItemCount.text = "${order.items.size} items"
            
            itemView.setOnClickListener { onOrderClick(order) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_order, parent, false)
        return OrderViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        holder.bind(orders[position], onOrderClick)
    }

    override fun getItemCount(): Int = orders.size

    fun updateOrders(newOrders: List<Order>) {
        orders = newOrders
        notifyDataSetChanged()
    }
}

package com.campuspinduoduo.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import com.campuspinduoduo.model.Pool
import com.campuspinduoduo.R

class PoolAdapter(
    private var pools: List<Pool> = emptyList(),
    private val onPoolClick: (Pool) -> Unit,
    private val onJoinClick: (Pool) -> Unit
) : RecyclerView.Adapter<PoolAdapter.PoolViewHolder>() {

    class PoolViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        val poolName: TextView = itemView.findViewById(R.id.pool_name)
        val poolGoal: TextView = itemView.findViewById(R.id.pool_goal)
        val poolProgress: ProgressBar = itemView.findViewById(R.id.pool_progress)
        val poolMembers: TextView = itemView.findViewById(R.id.pool_members)
        val poolStatus: TextView = itemView.findViewById(R.id.pool_status)
        val joinButton: Button = itemView.findViewById(R.id.btn_join_pool)

        fun bind(pool: Pool, onPoolClick: (Pool) -> Unit, onJoinClick: (Pool) -> Unit) {
            poolName.text = pool.poolName
            poolGoal.text = "Goal: ₦${String.format("%.2f", pool.goal)}"
            poolMembers.text = "Members: ${pool.members}"
            poolStatus.text = pool.status.name
            
            val progress = ((pool.currentAmount / pool.goal) * 100).toInt()
            poolProgress.progress = progress
            
            itemView.setOnClickListener { onPoolClick(pool) }
            joinButton.setOnClickListener { onJoinClick(pool) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PoolViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_pool, parent, false)
        return PoolViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: PoolViewHolder, position: Int) {
        holder.bind(pools[position], onPoolClick, onJoinClick)
    }

    override fun getItemCount(): Int = pools.size

    fun updatePools(newPools: List<Pool>) {
        pools = newPools
        notifyDataSetChanged()
    }
}

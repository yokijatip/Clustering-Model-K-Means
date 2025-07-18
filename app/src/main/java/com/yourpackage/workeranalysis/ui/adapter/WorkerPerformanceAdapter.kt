package com.yourpackage.workeranalysis.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.yourpackage.workeranalysis.R
import com.yourpackage.workeranalysis.data.WorkerPerformanceData
import com.yourpackage.workeranalysis.databinding.ItemWorkerPerformanceBinding

class WorkerPerformanceAdapter : ListAdapter<WorkerPerformanceData, WorkerPerformanceAdapter.ViewHolder>(DiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemWorkerPerformanceBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class ViewHolder(private val binding: ItemWorkerPerformanceBinding) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(worker: WorkerPerformanceData) {
            binding.apply {
                tvWorkerName.text = worker.name
                tvWorkerEmail.text = worker.email
                tvWorkerId.text = "ID: ${worker.workerId}"
                
                tvAttendanceRate.text = "${worker.attendanceRate.toInt()}%"
                tvAvgWorkHours.text = String.format("%.1f hrs", worker.avgWorkHours)
                tvPunctualityScore.text = "${worker.punctualityScore.toInt()}%"
                tvConsistencyScore.text = "${worker.consistencyScore.toInt()}%"
                
                tvPerformanceLabel.text = worker.performanceLabel
                tvConfidence.text = String.format("Confidence: %.1f%%", worker.confidence * 100)
                
                // Set performance label color
                val labelColor = when (worker.performanceLabel) {
                    "High Performer" -> ContextCompat.getColor(root.context, R.color.high_performer_color)
                    "Medium Performer" -> ContextCompat.getColor(root.context, R.color.medium_performer_color)
                    "Low Performer" -> ContextCompat.getColor(root.context, R.color.low_performer_color)
                    else -> ContextCompat.getColor(root.context, R.color.medium_performer_color)
                }
                
                tvPerformanceLabel.setTextColor(labelColor)
                cardPerformanceIndicator.setCardBackgroundColor(labelColor)
            }
        }
    }
    
    class DiffCallback : DiffUtil.ItemCallback<WorkerPerformanceData>() {
        override fun areItemsTheSame(oldItem: WorkerPerformanceData, newItem: WorkerPerformanceData): Boolean {
            return oldItem.userId == newItem.userId
        }
        
        override fun areContentsTheSame(oldItem: WorkerPerformanceData, newItem: WorkerPerformanceData): Boolean {
            return oldItem == newItem
        }
    }
}
package com.yourpackage.workeranalysis.ui

import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.yourpackage.workeranalysis.databinding.ActivityWorkerAnalysisBinding
import com.yourpackage.workeranalysis.ui.adapter.WorkerPerformanceAdapter
import com.yourpackage.workeranalysis.viewmodel.WorkerAnalysisViewModel
import kotlinx.coroutines.launch

class WorkerAnalysisActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityWorkerAnalysisBinding
    private val viewModel: WorkerAnalysisViewModel by viewModels()
    private lateinit var adapter: WorkerPerformanceAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityWorkerAnalysisBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupObservers()
        showDateRangePicker()
    }
    
    private fun setupUI() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Worker Performance Analysis"
        
        adapter = WorkerPerformanceAdapter()
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        binding.recyclerView.adapter = adapter
        
        binding.fabRefresh.setOnClickListener {
            showDateRangePicker()
        }
    }
    
    private fun setupObservers() {
        viewModel.workerPerformanceData.observe(this) { data ->
            adapter.submitList(data)
            updateSummaryCards(data)
        }
        
        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            binding.recyclerView.visibility = if (isLoading) View.GONE else View.VISIBLE
        }
        
        viewModel.error.observe(this) { error ->
            if (error.isNotEmpty()) {
                binding.tvError.text = error
                binding.tvError.visibility = View.VISIBLE
                binding.recyclerView.visibility = View.GONE
            } else {
                binding.tvError.visibility = View.GONE
            }
        }
    }
    
    private fun showDateRangePicker() {
        val dateRangePicker = DateRangePickerDialog(this) { startDate, endDate ->
            binding.tvDateRange.text = "Analysis Period: $startDate to $endDate"
            lifecycleScope.launch {
                viewModel.analyzeWorkerPerformance(startDate, endDate)
            }
        }
        dateRangePicker.show()
    }
    
    private fun updateSummaryCards(data: List<com.yourpackage.workeranalysis.data.WorkerPerformanceData>) {
        if (data.isEmpty()) return
        
        val highPerformers = data.count { it.performanceLabel == "High Performer" }
        val mediumPerformers = data.count { it.performanceLabel == "Medium Performer" }
        val lowPerformers = data.count { it.performanceLabel == "Low Performer" }
        
        binding.tvHighPerformers.text = highPerformers.toString()
        binding.tvMediumPerformers.text = mediumPerformers.toString()
        binding.tvLowPerformers.text = lowPerformers.toString()
        binding.tvTotalWorkers.text = data.size.toString()
        
        // Calculate averages
        val avgAttendance = data.map { it.attendanceRate }.average()
        val avgWorkHours = data.map { it.avgWorkHours }.average()
        val avgPunctuality = data.map { it.punctualityScore }.average()
        val avgConsistency = data.map { it.consistencyScore }.average()
        
        binding.tvAvgAttendance.text = String.format("%.1f%%", avgAttendance)
        binding.tvAvgWorkHours.text = String.format("%.1f hrs", avgWorkHours)
        binding.tvAvgPunctuality.text = String.format("%.1f%%", avgPunctuality)
        binding.tvAvgConsistency.text = String.format("%.1f%%", avgConsistency)
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
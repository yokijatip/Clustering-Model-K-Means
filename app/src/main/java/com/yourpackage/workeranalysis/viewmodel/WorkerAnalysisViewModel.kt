package com.yourpackage.workeranalysis.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.yourpackage.workeranalysis.data.WorkerPerformanceData
import com.yourpackage.workeranalysis.ml.WorkerAnalysisMLModel
import com.yourpackage.workeranalysis.repository.WorkerRepository
import kotlinx.coroutines.launch

class WorkerAnalysisViewModel(application: Application) : AndroidViewModel(application) {
    
    private val repository = WorkerRepository()
    private val mlModel = WorkerAnalysisMLModel(application)
    
    private val _workerPerformanceData = MutableLiveData<List<WorkerPerformanceData>>()
    val workerPerformanceData: LiveData<List<WorkerPerformanceData>> = _workerPerformanceData
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error
    
    suspend fun analyzeWorkerPerformance(startDate: String, endDate: String) {
        _isLoading.value = true
        _error.value = ""
        
        viewModelScope.launch {
            try {
                // Download and load ML model
                val modelLoaded = mlModel.downloadAndLoadModel()
                if (!modelLoaded) {
                    _error.value = "Failed to load ML model from Firebase"
                    _isLoading.value = false
                    return@launch
                }
                
                // Fetch data from Firestore
                val workers = repository.getWorkersInDateRange(startDate, endDate)
                val attendance = repository.getAttendanceInDateRange(startDate, endDate)
                
                if (workers.isEmpty()) {
                    _error.value = "No workers found in the selected date range"
                    _isLoading.value = false
                    return@launch
                }
                
                // Calculate performance metrics
                val performanceData = repository.calculateWorkerPerformance(
                    workers, attendance, startDate, endDate
                )
                
                // Run ML predictions
                val finalData = performanceData.map { worker ->
                    val (performanceLabel, confidence) = mlModel.predict(
                        worker.attendanceRate,
                        worker.avgWorkHours,
                        worker.punctualityScore,
                        worker.consistencyScore
                    )
                    
                    val cluster = when (performanceLabel) {
                        "High Performer" -> 2
                        "Medium Performer" -> 1
                        "Low Performer" -> 0
                        else -> -1
                    }
                    
                    worker.copy(
                        performanceLabel = performanceLabel,
                        cluster = cluster,
                        confidence = confidence
                    )
                }
                
                _workerPerformanceData.value = finalData
                _isLoading.value = false
                
            } catch (e: Exception) {
                _error.value = "Error analyzing worker performance: ${e.message}"
                _isLoading.value = false
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        mlModel.close()
    }
}
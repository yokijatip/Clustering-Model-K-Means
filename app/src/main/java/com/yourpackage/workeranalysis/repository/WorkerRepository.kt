package com.yourpackage.workeranalysis.repository

import android.util.Log
import com.google.firebase.firestore.FirebaseFirestore
import com.yourpackage.workeranalysis.data.AttendanceRecord
import com.yourpackage.workeranalysis.data.User
import com.yourpackage.workeranalysis.data.WorkerPerformanceData
import kotlinx.coroutines.tasks.await
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.abs

class WorkerRepository {
    
    private val firestore = FirebaseFirestore.getInstance()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    
    suspend fun getWorkersInDateRange(startDate: String, endDate: String): List<User> {
        return try {
            val snapshot = firestore.collection("users")
                .whereEqualTo("role", "worker")
                .get()
                .await()
            
            snapshot.documents.mapNotNull { doc ->
                doc.toObject(User::class.java)?.copy(userId = doc.id)
            }
        } catch (e: Exception) {
            Log.e("WorkerRepository", "Error fetching workers: ${e.message}")
            emptyList()
        }
    }
    
    suspend fun getAttendanceInDateRange(startDate: String, endDate: String): List<AttendanceRecord> {
        return try {
            val snapshot = firestore.collection("attendance")
                .whereGreaterThanOrEqualTo("date", startDate)
                .whereLessThanOrEqualTo("date", endDate)
                .whereEqualTo("status", "approved")
                .get()
                .await()
            
            snapshot.documents.mapNotNull { doc ->
                doc.toObject(AttendanceRecord::class.java)?.copy(attendanceId = doc.id)
            }
        } catch (e: Exception) {
            Log.e("WorkerRepository", "Error fetching attendance: ${e.message}")
            emptyList()
        }
    }
    
    fun calculateWorkerPerformance(
        workers: List<User>,
        attendance: List<AttendanceRecord>,
        startDate: String,
        endDate: String
    ): List<WorkerPerformanceData> {
        
        val workingDays = calculateWorkingDays(startDate, endDate)
        
        return workers.map { worker ->
            val workerAttendance = attendance.filter { it.userId == worker.userId }
            
            val attendanceRate = calculateAttendanceRate(workerAttendance, workingDays)
            val avgWorkHours = calculateAvgWorkHours(workerAttendance)
            val punctualityScore = calculatePunctualityScore(workerAttendance)
            val consistencyScore = calculateConsistencyScore(workerAttendance)
            
            WorkerPerformanceData(
                userId = worker.userId,
                name = worker.name,
                email = worker.email,
                workerId = worker.workerId,
                attendanceRate = attendanceRate,
                avgWorkHours = avgWorkHours,
                punctualityScore = punctualityScore,
                consistencyScore = consistencyScore
            )
        }
    }
    
    private fun calculateAttendanceRate(attendance: List<AttendanceRecord>, workingDays: Int): Float {
        if (workingDays == 0) return 0f
        return (attendance.size.toFloat() / workingDays.toFloat() * 100f).coerceAtMost(100f)
    }
    
    private fun calculateAvgWorkHours(attendance: List<AttendanceRecord>): Float {
        if (attendance.isEmpty()) return 0f
        val totalHours = attendance.sumOf { it.workMinutes } / 60.0
        return (totalHours / attendance.size).toFloat()
    }
    
    private fun calculatePunctualityScore(attendance: List<AttendanceRecord>): Float {
        if (attendance.isEmpty()) return 0f
        
        val punctualDays = attendance.count { record ->
            isPunctual(record.clockInTime)
        }
        
        return (punctualDays.toFloat() / attendance.size.toFloat() * 100f)
    }
    
    private fun calculateConsistencyScore(attendance: List<AttendanceRecord>): Float {
        if (attendance.size < 2) return 0f
        
        val workHours = attendance.map { it.workMinutes / 60.0 }
        val mean = workHours.average()
        val variance = workHours.map { (it - mean) * (it - mean) }.average()
        val stdDev = kotlin.math.sqrt(variance)
        
        // Convert to consistency score (lower std_dev = higher consistency)
        val maxStd = 4.0 // Assume max std deviation of 4 hours
        val consistencyScore = ((maxStd - stdDev) / maxStd * 100).coerceAtLeast(0.0)
        
        return consistencyScore.toFloat()
    }
    
    private fun isPunctual(clockInTime: String): Boolean {
        return try {
            // Parse time string (format: "2024-12-19T09:43:30Z" or similar)
            val timePart = clockInTime.split("T")[1].split(":")[0].toInt()
            timePart <= 7 // Punctual if clock in at 7 AM or earlier
        } catch (e: Exception) {
            false
        }
    }
    
    private fun calculateWorkingDays(startDate: String, endDate: String): Int {
        return try {
            val start = dateFormat.parse(startDate) ?: return 0
            val end = dateFormat.parse(endDate) ?: return 0
            
            val calendar = Calendar.getInstance()
            calendar.time = start
            
            var workingDays = 0
            while (calendar.time <= end) {
                val dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
                if (dayOfWeek != Calendar.SATURDAY && dayOfWeek != Calendar.SUNDAY) {
                    workingDays++
                }
                calendar.add(Calendar.DAY_OF_MONTH, 1)
            }
            
            workingDays
        } catch (e: Exception) {
            Log.e("WorkerRepository", "Error calculating working days: ${e.message}")
            0
        }
    }
}
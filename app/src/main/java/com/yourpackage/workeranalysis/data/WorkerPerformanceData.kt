package com.yourpackage.workeranalysis.data

data class WorkerPerformanceData(
    val userId: String = "",
    val name: String = "",
    val email: String = "",
    val workerId: String = "",
    val attendanceRate: Float = 0f,
    val avgWorkHours: Float = 0f,
    val punctualityScore: Float = 0f,
    val consistencyScore: Float = 0f,
    val performanceLabel: String = "",
    val cluster: Int = -1,
    val confidence: Float = 0f
)

data class AttendanceRecord(
    val attendanceId: String = "",
    val userId: String = "",
    val date: String = "",
    val clockInTime: String = "",
    val clockOutTime: String = "",
    val workMinutes: Long = 0,
    val overtimeMinutes: Long = 0,
    val status: String = ""
)

data class User(
    val userId: String = "",
    val name: String = "",
    val email: String = "",
    val role: String = "",
    val workerId: String = ""
)
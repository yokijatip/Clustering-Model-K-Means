package com.yourpackage.workeranalysis.ml

import android.content.Context
import android.util.Log
import com.google.firebase.ml.modeldownloader.CustomModel
import com.google.firebase.ml.modeldownloader.CustomModelDownloadConditions
import com.google.firebase.ml.modeldownloader.DownloadType
import com.google.firebase.ml.modeldownloader.FirebaseModelDownloader
import kotlinx.coroutines.tasks.await
import org.tensorflow.lite.Interpreter
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

class WorkerAnalysisMLModel(private val context: Context) {
    
    private var interpreter: Interpreter? = null
    private val modelName = "worker_analysis_model" // Nama model di Firebase ML
    
    // Model metadata (sesuai dengan tflite_model_info.json)
    private val scalerMean = floatArrayOf(0.7259528f, 2.102609f, 8.102073f, 16.519678f)
    private val scalerScale = floatArrayOf(1.526985f, 3.154934f, 23.178580f, 32.830153f)
    
    private val performanceMapping = mapOf(
        0 to "Low Performer",
        1 to "Medium Performer",
        2 to "High Performer"
    )
    
    suspend fun downloadAndLoadModel(): Boolean {
        return try {
            val conditions = CustomModelDownloadConditions.Builder()
                .requireWifi()
                .build()
            
            val downloadedModel: CustomModel = FirebaseModelDownloader.getInstance()
                .getModel(modelName, DownloadType.LOCAL_MODEL_UPDATE_IN_BACKGROUND, conditions)
                .await()
            
            val modelFile = downloadedModel.file
            if (modelFile != null) {
                interpreter = Interpreter(modelFile)
                Log.d("MLModel", "Model loaded successfully")
                true
            } else {
                Log.e("MLModel", "Model file is null")
                false
            }
        } catch (e: Exception) {
            Log.e("MLModel", "Error loading model: ${e.message}")
            false
        }
    }
    
    fun predict(
        attendanceRate: Float,
        avgWorkHours: Float,
        punctualityScore: Float,
        consistencyScore: Float
    ): Pair<String, Float> {
        
        val interpreter = this.interpreter ?: return Pair("Unknown", 0f)
        
        try {
            // Normalize input features (StandardScaler equivalent)
            val normalizedFeatures = floatArrayOf(
                (attendanceRate - scalerMean[0]) / scalerScale[0],
                (avgWorkHours - scalerMean[1]) / scalerScale[1],
                (punctualityScore - scalerMean[2]) / scalerScale[2],
                (consistencyScore - scalerMean[3]) / scalerScale[3]
            )
            
            // Prepare input buffer
            val inputBuffer = ByteBuffer.allocateDirect(4 * 4) // 4 features * 4 bytes each
            inputBuffer.order(ByteOrder.nativeOrder())
            normalizedFeatures.forEach { inputBuffer.putFloat(it) }
            
            // Prepare output buffers
            val clusterOutput = ByteBuffer.allocateDirect(4) // 1 float
            clusterOutput.order(ByteOrder.nativeOrder())
            
            val distanceOutput = ByteBuffer.allocateDirect(4) // 1 float
            distanceOutput.order(ByteOrder.nativeOrder())
            
            // Run inference
            val outputs = mapOf(
                0 to clusterOutput,
                1 to distanceOutput
            )
            
            interpreter.runForMultipleInputsOutputs(arrayOf(inputBuffer), outputs)
            
            // Get results
            clusterOutput.rewind()
            distanceOutput.rewind()
            
            val predictedCluster = clusterOutput.float.toInt()
            val distance = distanceOutput.float
            
            // Convert distance to confidence (inverse relationship)
            val confidence = 1f / (1f + distance)
            
            val performanceLabel = performanceMapping[predictedCluster] ?: "Unknown"
            
            Log.d("MLModel", "Prediction: $performanceLabel (Cluster: $predictedCluster, Confidence: $confidence)")
            
            return Pair(performanceLabel, confidence)
            
        } catch (e: Exception) {
            Log.e("MLModel", "Error during prediction: ${e.message}")
            return Pair("Error", 0f)
        }
    }
    
    fun close() {
        interpreter?.close()
        interpreter = null
    }
}
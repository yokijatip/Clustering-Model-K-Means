package com.yourpackage.workeranalysis

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.yourpackage.workeranalysis.databinding.ActivityMainBinding
import com.yourpackage.workeranalysis.ui.WorkerAnalysisActivity

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        binding.btnWorkerAnalysis.setOnClickListener {
            startActivity(Intent(this, WorkerAnalysisActivity::class.java))
        }
    }
}
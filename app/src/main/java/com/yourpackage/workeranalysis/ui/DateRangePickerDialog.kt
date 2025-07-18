package com.yourpackage.workeranalysis.ui

import android.app.DatePickerDialog
import android.content.Context
import android.content.DialogInterface
import androidx.appcompat.app.AlertDialog
import com.google.android.material.button.MaterialButton
import com.google.android.material.textview.MaterialTextView
import com.yourpackage.workeranalysis.R
import java.text.SimpleDateFormat
import java.util.*

class DateRangePickerDialog(
    private val context: Context,
    private val onDateRangeSelected: (startDate: String, endDate: String) -> Unit
) {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("dd MMM yyyy", Locale.getDefault())
    
    private var startDate: Calendar? = null
    private var endDate: Calendar? = null
    
    fun show() {
        val dialogView = android.view.LayoutInflater.from(context)
            .inflate(R.layout.dialog_date_range_picker, null)
        
        val startDateText = dialogView.findViewById<MaterialTextView>(R.id.tvStartDate)
        val endDateText = dialogView.findViewById<MaterialTextView>(R.id.tvEndDate)
        val selectStartDateBtn = dialogView.findViewById<MaterialButton>(R.id.btnSelectStartDate)
        val selectEndDateBtn = dialogView.findViewById<MaterialButton>(R.id.btnSelectEndDate)
        
        // Set default dates (last 30 days)
        val today = Calendar.getInstance()
        endDate = today.clone() as Calendar
        startDate = (today.clone() as Calendar).apply {
            add(Calendar.DAY_OF_MONTH, -30)
        }
        
        updateDateTexts(startDateText, endDateText)
        
        selectStartDateBtn.setOnClickListener {
            showDatePicker(true) { selectedDate ->
                startDate = selectedDate
                updateDateTexts(startDateText, endDateText)
            }
        }
        
        selectEndDateBtn.setOnClickListener {
            showDatePicker(false) { selectedDate ->
                endDate = selectedDate
                updateDateTexts(startDateText, endDateText)
            }
        }
        
        AlertDialog.Builder(context)
            .setTitle("Select Date Range")
            .setView(dialogView)
            .setPositiveButton("Analyze") { _, _ ->
                val start = startDate?.let { dateFormat.format(it.time) } ?: ""
                val end = endDate?.let { dateFormat.format(it.time) } ?: ""
                if (start.isNotEmpty() && end.isNotEmpty()) {
                    onDateRangeSelected(start, end)
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun showDatePicker(isStartDate: Boolean, onDateSelected: (Calendar) -> Unit) {
        val calendar = if (isStartDate) startDate ?: Calendar.getInstance() 
                      else endDate ?: Calendar.getInstance()
        
        DatePickerDialog(
            context,
            { _, year, month, dayOfMonth ->
                val selectedCalendar = Calendar.getInstance().apply {
                    set(year, month, dayOfMonth)
                }
                onDateSelected(selectedCalendar)
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        ).show()
    }
    
    private fun updateDateTexts(startDateText: MaterialTextView, endDateText: MaterialTextView) {
        startDate?.let {
            startDateText.text = displayDateFormat.format(it.time)
        }
        endDate?.let {
            endDateText.text = displayDateFormat.format(it.time)
        }
    }
}
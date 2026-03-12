package com.campuspinduoduo.ui.activities

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import com.campuspinduoduo.R

class ProfileActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        initializeProfile()
        setupSaveButton()
    }

    private fun initializeProfile() {
        // Load user profile data (in production would come from API)
        findViewById<TextView>(R.id.profile_user_name)?.text = "John Doe"
        findViewById<TextView>(R.id.profile_user_email)?.text = "john@example.com"
        findViewById<TextView>(R.id.profile_user_phone)?.text = "08012345678"
        findViewById<TextView>(R.id.profile_total_orders)?.text = "5"
        findViewById<TextView>(R.id.profile_total_spent)?.text = "₦125,000"
        findViewById<TextView>(R.id.profile_rating)?.text = "4.8"
    }

    private fun setupSaveButton() {
        findViewById<Button>(R.id.btn_save_profile)?.setOnClickListener {
            val name = findViewById<EditText>(R.id.edit_user_name)?.text.toString()
            val email = findViewById<EditText>(R.id.edit_user_email)?.text.toString()
            val phone = findViewById<EditText>(R.id.edit_user_phone)?.text.toString()

            if (name.isNullOrEmpty() || email.isNullOrEmpty()) {
                Toast.makeText(this, "Please fill in required fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Save profile in production
            Toast.makeText(this, "Profile updated!", Toast.LENGTH_SHORT).show()
        }
    }
}

# 🩺 HealthSYNQ-D

### Smartwatch-Based Adaptive Diet and Glucose Management System

---

## 📌 Project Overview

**HealthSYNQ-D** is an AI-assisted health management system designed for **diabetic and pre-diabetic individuals**, especially in the Indian context.

The system integrates:

* 📊 Blood glucose monitoring
* ⌚ Smartwatch lifestyle data
* 🥗 Intelligent diet recommendation

to provide **adaptive, personalized, and non-repetitive diet plans** that help users manage and gradually reduce their blood sugar levels.

---

## 🚨 Problem Statement

Diabetes is increasing rapidly among Indian youth due to:

* Sedentary lifestyle
* High carbohydrate intake
* Poor sleep habits

Most existing systems:

* Provide **static diet plans**
* Do not adapt to daily health changes
* Ignore lifestyle factors like activity and sleep

👉 HealthSYNQ-D solves this by providing **dynamic, data-driven diet recommendations**.

---

## 🎯 Objectives

The system aims to:

* Track blood sugar levels (fasting & post-meal)
* Integrate smartwatch data (steps, sleep, heart rate)
* Generate **adaptive and non-repetitive diet plans**
* Assist users in gradually reducing glucose levels
* Provide actionable health insights

---

## 🔄 System Workflow

1. **User Registration**

   * Profile details (age, weight, health status)

2. **Goal Setting**

   * Example: Reduce glucose from 400 → 250 in 3 months

3. **Daily Data Input**

   * Glucose readings (manual)
   * Smartwatch data (steps, sleep, HR)

4. **Backend Processing**

   * Analyze trends
   * Compute daily carb allowance

5. **Diet Recommendation**

   * Breakfast, lunch, dinner, snacks
   * Personalized and non-repetitive

6. **Weekly Evaluation**

   * Compare progress
   * Adjust diet dynamically

---

## 📊 Data Collection

### 1. Glucose Data

* Fasting sugar
* Post-meal sugar

### 2. Smartwatch Data

* Steps
* Sleep duration
* Heart rate
* Activity level

### 3. Food Dataset

* Macronutrients (carbs, protein, fat, fiber)
* Calories
* Glycemic Index (GI)
* Food category

---

## 🥗 Food Dataset Structure

Each food item includes:

* Carbohydrates
* Protein
* Fat
* Fiber
* Calories
* Glycemic Index
* Meal type (breakfast/lunch/dinner/snack)
* Category (rice-based, millet-based, vegan, etc.)

---

## ⚙️ Diet Recommendation Engine

The system dynamically generates diets using:

* **Carb Adjustment**

  * High sugar → lower carbs
  * Stable sugar → balanced carbs

* **Food Filtering**

  * Based on meal type and constraints

* **Scoring System**

  * Low GI → higher priority
  * High protein/fiber → better

* **Non-Repetition Logic**

  * Avoids recent meals

* **Randomized Selection**

  * Ensures variety

---

## 🔁 Alternative Food Suggestion

If a user rejects a meal:

* Suggests alternatives with:

  * Similar calories
  * Lower/equal GI
  * Comparable protein

---

## 🔄 Non-Repetition Mechanism

* Tracks last 7 days of meals
* Penalizes repeated foods
* Rotates food categories

---

## 📅 Weekly Adjustment System

* Compares expected vs actual glucose reduction

* Adjusts:

  * Carb limits
  * Macro ratios

* Tightens or relaxes diet accordingly

---

## 📈 Prediction Module

A simple ML model (e.g., Linear Regression) is used to:

* Predict glucose trends:

  * Increasing
  * Decreasing
  * Stable

### Inputs:

* Previous glucose values
* Activity (steps)
* Sleep
* Diet patterns

---

## 🤖 AI Chatbot

* Answers food and health-related queries
* Provides personalized suggestions
* Uses real-time user data

**Example:**

> “You had high sugar today → go for a 20-minute walk”

---

## ⌚ Smartwatch Integration

Enhances recommendations using:

* Low activity → stricter diet
* Good sleep → improved glucose stability
* Active days → slightly flexible diet

---

## 🛠️ Technology Stack

| Layer            | Technology            |
| ---------------- | --------------------- |
| Frontend         | Kotlin       
| Backend          | SpringBoot / Django      |
| Database         | PostgreSQL            |
| Machine Learning | Python (scikit-learn) |
| Data Processing  | pandas                |

---

## ✨ Key Features

* Adaptive diet planning
* Non-repetitive meal generation
* Goal-based glucose tracking
* Smartwatch integration
* AI chatbot support
* Weekly feedback loop

---

## 🚀 Novelty & Contribution

* Combines **glucose + wearable + diet data**
* Dynamic carb adjustment system
* Focused on **Indian dietary patterns**
* Uses **Explainable AI (not black-box)**

---

## 📌 Future Scope

* Real-time smartwatch API integration
* Mobile app deployment
* Advanced ML models (LSTM, time-series forecasting)
* Integration with hospitals/clinics

---

## 🏁 Conclusion

HealthSYNQ-D provides a **practical, personalized, and scalable solution** for diabetes management by:

* Using real-time health data
* Continuously adapting diet plans
* Encouraging sustainable lifestyle improvements


## 📜 License

This project is for academic purposes.



⭐ *If you find this project useful, consider giving it a star!*

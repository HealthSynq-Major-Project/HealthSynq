package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dao.HealthDAO;
import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.HealthDTO;
import com.health.HealthSynqBackend.entities.*;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.Map;

@Service
public class HealthServiceImpl implements HealthService{
    private HealthDAO healthDAO;
    public HealthServiceImpl(HealthDAO healthDAO){
        this.healthDAO = healthDAO;

    }
    @Override
    @Transactional
    public GenericResponse processHealthData(int userId, HealthDTO healthDTO){
        validateHealthData(healthDTO);

        Users user = healthDAO.findUserById(userId);

        if(user==null){
            throw new GenericBadRequestException("User not Found");
        }

        LocalDate today = LocalDate.now();

        DailyHealthData existing = healthDAO.findUserByIdAndDate(user, today);

        if (existing == null) {
            DailyHealthData data = new DailyHealthData(
                    user,
                    today,
                    healthDTO.getSteps(),
                    healthDTO.getHeartRateAvg(),
                    healthDTO.getCaloriesBurned(),
                    healthDTO.getSleepHours(),
                    healthDTO.getSpO2()
            );

            data.setCreatedAt(LocalDateTime.now());
            data.setUpdatedAt(LocalDateTime.now());

            healthDAO.saveDailyHealthData(data);

        } else {
            if (healthDTO.getSteps() != null)
                existing.setSteps(healthDTO.getSteps());

            if (healthDTO.getHeartRateAvg() != null)
                existing.setHeartRateAvg(healthDTO.getHeartRateAvg());

            if (healthDTO.getCaloriesBurned() != null)
                existing.setCaloriesBurned(healthDTO.getCaloriesBurned());

            if (healthDTO.getSleepHours() != null)
                existing.setSleepHours(healthDTO.getSleepHours());

            if (healthDTO.getSpO2() != null)
                existing.setSpO2(healthDTO.getSpO2());

            existing.setUpdatedAt(LocalDateTime.now());

            healthDAO.saveDailyHealthData(existing);
        }

        UserCurrentHealth current = healthDAO.findUser(user);

        if (current == null) {
            current = new UserCurrentHealth(user);
            current.setCreatedAt(LocalDateTime.now());
        }

        if (healthDTO.getSteps() != null)
            current.setSteps(healthDTO.getSteps());

        if (healthDTO.getHeartRateAvg() != null)
            current.setHeartRateAvg(healthDTO.getHeartRateAvg());

        if (healthDTO.getCaloriesBurned() != null)
            current.setCaloriesBurned(healthDTO.getCaloriesBurned());

        if (healthDTO.getSleepHours() != null)
            current.setSleepHours(healthDTO.getSleepHours());

        if (healthDTO.getSpO2() != null)
            current.setSpO2(healthDTO.getSpO2());

        UserGoal userGoal = healthDAO.findGoalByUserId(userId);

        if(userGoal==null){
            throw new GenericBadRequestException("User Goal not found");
        }

        LocalDateTime startDate = userGoal.getStartDate();

        if(startDate==null){
            startDate = userGoal.getCreatedAt();
        }

        long daysPassed = ChronoUnit.DAYS.between(
                startDate.toLocalDate(),
                LocalDate.now()
        );

        long daysLeft = userGoal.getTargetDuration() - daysPassed;

        if (daysLeft <= 0) {
            daysLeft = 1;
        }

        UserProfile userProfile = healthDAO.findUserProfileByUser(user);

        if(userProfile==null){
            throw new GenericBadRequestException("User Profile not Found");
        }

        int kcal = calculateDailyKcal(userProfile, current, userGoal,(int) daysLeft);

        current.setDailyKcal(kcal);
        current.setUpdatedAt(LocalDateTime.now());

        healthDAO.saveUserCurrentHealth(current);

        Map<String, Object> data = new HashMap<>();

        data.put("dailyKcal", current.getDailyKcal());
        data.put("steps", current.getSteps());
        data.put("heartRateAvg", current.getHeartRateAvg());
        data.put("caloriesBurned", current.getCaloriesBurned());
        data.put("sleepHours", current.getSleepHours());
        data.put("spO2", current.getSpO2());
        data.put("glucoseLevel", current.getGlucoseLevel());
        data.put("dietPreference", current.getDietPreference());

        return new GenericResponse(
                true,
                "Health data processed successfully",
                200,
                data
        );
    }

    private int calculateDailyKcal(UserProfile profile,
                                   UserCurrentHealth current,
                                   UserGoal goal,
                                   int daysLeft) {

        // 🔹 BASIC USER DATA
        double weightKg = profile.getWeight() / 1000.0;
        int height = profile.getHeight();
        int age = profile.getAge();
        String gender = profile.getGender();

        double goalWeightKg = goal.getTargetWeight() / 1000.0;

        // 🔹 STEP 1: BMR
        double bmr;
        if ("male".equalsIgnoreCase(gender)) {
            bmr = 10 * weightKg + 6.25 * height - 5 * age + 5;
        } else {
            bmr = 10 * weightKg + 6.25 * height - 5 * age - 161;
        }

        // 🔹 STEP 2: Weight change required
        double weightChange = goalWeightKg - weightKg;

        // 🔹 STEP 3: Weekly weight change (based on daysLeft)
        double safeDays = Math.max(daysLeft, 7);

        double weeklyChange = Math.abs(weightChange) / (safeDays / 7.0);


        double activityFactor;
        if (weeklyChange < 0.25) {
            activityFactor = 1.2;
        } else if (weeklyChange < 0.5) {
            activityFactor = 1.375;
        } else if (weeklyChange < 1.0) {
            activityFactor = 1.55;
        } else if (weeklyChange < 1.5) {
            activityFactor = 1.725;
        } else {
            activityFactor = 1.9;
        }

        // 🔹 STEP 4: TDEE
        double tdee = bmr * activityFactor;

        // 🔹 STEP 5: Total calorie change (7700 kcal per kg)
        double totalCalorieChange = weightChange * 7700;

        // 🔹 STEP 6: Daily calorie adjustment (IMPORTANT CHANGE)
        double dailyCalorieChange = totalCalorieChange / daysLeft;

        // 🔹 STEP 7: Final calories
        double targetCalories = tdee + dailyCalorieChange;

        // 🔹 STEP 8: Safety clamp
        if ("male".equalsIgnoreCase(gender)) {
            targetCalories = Math.max(targetCalories, 1500);
        } else {
            targetCalories = Math.max(targetCalories, 1200);
        }

        return (int) Math.round(targetCalories);
    }

    private int getBaselineGlucose(Users user) {
        UserProfile userProfile = healthDAO.findUserProfileByUser(user);

        if (userProfile == null) {
            throw new GenericBadRequestException("User profile not found");
        }

        int age = userProfile.getAge();
        String gender = userProfile.getGender();

        int base;

        if (age < 18) base = 85;
        else if (age < 40) base = 90;
        else if (age < 60) base = 92;
        else base = 95;

        // VERY SMALL adjustment
        if ("female".equalsIgnoreCase(gender)) {
            base -= 2; // slightly lower
        }

        return base;
    }
    private void validateHealthData(HealthDTO dto) {

        if (dto.getSteps() != null) {
            if (dto.getSteps() < 0 || dto.getSteps() > 100000) {
                throw new GenericBadRequestException("Invalid steps count");
            }
        }

        if (dto.getHeartRateAvg() != null) {
            if (dto.getHeartRateAvg() < 30 || dto.getHeartRateAvg() > 220) {
                throw new GenericBadRequestException("Invalid heart rate");
            }
        }

        if (dto.getCaloriesBurned() != null) {
            if (dto.getCaloriesBurned() < 0 || dto.getCaloriesBurned() > 10000) {
                throw new GenericBadRequestException("Invalid calories burned");
            }
        }

        if (dto.getSleepHours() != null) {
            if (dto.getSleepHours() < 0 || dto.getSleepHours() > 24) {
                throw new GenericBadRequestException("Invalid sleep hours");
            }
        }

        if (dto.getSpO2() != null) {
            if (dto.getSpO2() < 50 || dto.getSpO2() > 100) {
                throw new GenericBadRequestException("Invalid SpO2 level");
            }
        }
    }
}

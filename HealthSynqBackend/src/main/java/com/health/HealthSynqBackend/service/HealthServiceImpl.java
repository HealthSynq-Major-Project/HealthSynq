package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dao.HealthDAO;
import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.GlucoseDTO;
import com.health.HealthSynqBackend.dto.GlucoseHistoryDTO;
import com.health.HealthSynqBackend.dto.HealthDTO;
import com.health.HealthSynqBackend.entities.*;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
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

        int kcal = calculateDailyKcal(userProfile, userGoal,(int) daysLeft);

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
                                   UserGoal goal,
                                   int daysLeft) {

        // STEP 1 : Basic User Data
        double currentWeightKg = profile.getWeight() / 1000.0;
        double targetWeightKg = goal.getTargetWeight() / 1000.0;

        int height = profile.getHeight();
        int age = profile.getAge();
        String gender = profile.getGender();

        // Prevent division by zero
        daysLeft = Math.max(daysLeft, 1);

        // STEP 2 : Calculate BMR (Mifflin-St Jeor Formula)
        double bmr;

        if ("male".equalsIgnoreCase(gender)) {
            bmr = (10 * currentWeightKg)
                    + (6.25 * height)
                    - (5 * age)
                    + 5;
        } else {
            bmr = (10 * currentWeightKg)
                    + (6.25 * height)
                    - (5 * age)
                    - 161;
        }

        // STEP 3 : Default Activity Factor
        // Later this can come from profile.getActivityLevel()
        double activityFactor = 1.375;

        // STEP 4 : Maintenance Calories
        double maintenanceCalories = bmr * activityFactor;

        // STEP 5 : Goal Based Adjustment
        double weightDifference = targetWeightKg - currentWeightKg;

        // Approx. calories required to gain/lose 1 kg
        double totalCalorieAdjustment = weightDifference * 7700;

        double dailyCalorieAdjustment =
                totalCalorieAdjustment / daysLeft;

        // STEP 6 : Final Daily Target
        double targetCalories =
                maintenanceCalories + dailyCalorieAdjustment;

        // STEP 7 : Safety Limits
        if ("male".equalsIgnoreCase(gender)) {

            if (targetCalories < 1500) {
                targetCalories = 1500;
            }

            if (targetCalories > 3200) {
                targetCalories = 3200;
            }

        } else {

            if (targetCalories < 1200) {
                targetCalories = 1200;
            }

            if (targetCalories > 2800) {
                targetCalories = 2800;
            }
        }

        // Debug Logs (Remove Later)
        System.out.println("\n========== DAILY KCAL CALCULATION ==========");
        System.out.println("Current Weight : " + currentWeightKg + " kg");
        System.out.println("Target Weight  : " + targetWeightKg + " kg");
        System.out.println("Height         : " + height + " cm");
        System.out.println("Age            : " + age);
        System.out.println("Gender         : " + gender);
        System.out.println("Days Left      : " + daysLeft);
        System.out.println("BMR            : " + bmr);
        System.out.println("ActivityFactor : " + activityFactor);
        System.out.println("Maintenance    : " + maintenanceCalories);
        System.out.println("Daily Adjust   : " + dailyCalorieAdjustment);
        System.out.println("Target Kcal    : " + targetCalories);
        System.out.println("============================================\n");

        return (int) Math.round(targetCalories);
    }

    @Override
    @Transactional
    public GenericResponse updateGlucose(int userId, GlucoseDTO glucoseDTO){
        if(glucoseDTO==null || glucoseDTO.getGlucose()==null){
            throw new GenericBadRequestException("Glucose Level is required");
        }

        int glucose = glucoseDTO.getGlucose();

        if (glucose < 40 || glucose > 500) {
            throw new GenericBadRequestException("Invalid glucose level");
        }

        Users user = healthDAO.findUserById(userId);

        if(user==null){
            throw new GenericBadRequestException("User is not found");
        }

        UserGlucoseLog userGlucoseLog = new UserGlucoseLog();
        userGlucoseLog.setUsers(user);
        userGlucoseLog.setGlucoseLevel(glucose);
        userGlucoseLog.setCreatedAt(LocalDateTime.now());
        userGlucoseLog.setRecordedAt(LocalDateTime.now());

        healthDAO.saveGlucoseLog(userGlucoseLog);

        UserCurrentHealth userCurrentHealth = healthDAO.findUser(user);

        if(userCurrentHealth==null){
            userCurrentHealth = new UserCurrentHealth(user);
            userCurrentHealth.setCreatedAt(LocalDateTime.now());
        }

        userCurrentHealth.setGlucoseLevel(glucose);
        userCurrentHealth.setUpdatedAt(LocalDateTime.now());

        healthDAO.saveUserCurrentHealth(userCurrentHealth);

        List<UserGlucoseLog> glucoseLogs = healthDAO.findLastThreeGlucoseLogs(user);
        List<GlucoseHistoryDTO> history = new ArrayList<>();

        for (UserGlucoseLog log : glucoseLogs) {
            GlucoseHistoryDTO dto = new GlucoseHistoryDTO();
            dto.setGlucose(log.getGlucoseLevel());
            dto.setUnit("mg/dL");
            dto.setRecordedAt(log.getRecordedAt());
            history.add(dto);

        }

        Map<String, Object> data = new HashMap<>();

        data.put("last3Days", history);

        return new GenericResponse(
                true,
                "Glucose level updated successfully",
                200,
                data
        );
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

    public GenericResponse getUserProfile(int userId){
        Users theUser = healthDAO.findUserById(userId);

        if(theUser == null){
            throw new GenericBadRequestException("User not found");
        }

        UserProfile userProfile = healthDAO.findUserProfileByUser(theUser);

        if(userProfile == null){
            throw new GenericBadRequestException("Profile not found");
        }
        System.out.println("HEllo"+theUser);
        System.out.println(userProfile);

        Map<String,Object> healthData = new HashMap<>();

        healthData.put("email",theUser.getEmail());
        healthData.put("userName",theUser.getUserName());
        healthData.put("gender",userProfile.getGender());
        healthData.put("age",userProfile.getAge());
        healthData.put("height",userProfile.getHeight());
        healthData.put("weight",userProfile.getWeight());
        healthData.put("isDiabetic",userProfile.isDiabetic());

        return new GenericResponse(true,"User Profile Data",200,healthData);
    }

    @Override
    public GenericResponse getGlucoseHistory(int userId){
        Users user = healthDAO.findUserById(userId);
        if (user == null) {throw new GenericBadRequestException("User not found");}

        List<UserGlucoseLog> glucoseLogs = healthDAO.findLastThreeGlucoseLogs(user);

        List<GlucoseHistoryDTO> history = new ArrayList<>();

        for (UserGlucoseLog log : glucoseLogs) {
            GlucoseHistoryDTO dto = new GlucoseHistoryDTO();
            dto.setGlucose(log.getGlucoseLevel());
            dto.setUnit("mg/dL");
            dto.setRecordedAt(log.getRecordedAt());
            history.add(dto);
        }
        Map<String, Object> data = new HashMap<>();

        data.put("last3Days", history);

        return new GenericResponse(true,
                "Glucose history fetched successfully.",
                200,
                data
        );
    }

}

package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dao.HealthDAO;
import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.entities.UserCurrentHealth;
import com.health.HealthSynqBackend.entities.UserGlucoseLog;
import com.health.HealthSynqBackend.entities.UserProfile;
import com.health.HealthSynqBackend.entities.Users;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Repository;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Repository
public class DietServiceImpl implements DietService{
    private HealthDAO healthDAO;

    public DietServiceImpl(HealthDAO healthDAO){
        this.healthDAO = healthDAO;
    }
    @Override
    public GenericResponse generateDiet(int userId){
        Users user = healthDAO.findUserById(userId);

        if (user == null) {
            throw new GenericBadRequestException("User not found");
        }

        UserCurrentHealth current = healthDAO.findUser(user);

        if (current == null || current.getDailyKcal() == null) {

            throw new GenericBadRequestException("Health data not available");

        }

        UserProfile profile = healthDAO.findUserProfileByUser(user);

        if (profile == null) {
            throw new GenericBadRequestException("User profile not found");
        }

        Integer glucose = current.getGlucoseLevel();

        if (glucose == null) {
            UserGlucoseLog latest = healthDAO.findLatestGlucose(user);
            if (latest != null) {
                long hours = ChronoUnit.HOURS.between(
                        latest.getRecordedAt(),
                        LocalDateTime.now()
                );
                if (hours <= 24) {
                    glucose = latest.getGlucoseLevel();
                }
            }

            if (glucose == null) {
                glucose = getBaselineGlucose(user);
            }
        }

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("glucose_mg_dl", glucose);
        requestBody.put("daily_kcal", current.getDailyKcal());
        requestBody.put("diet", current.getDietPreference());

        RestTemplate restTemplate = new RestTemplate();
        String mlUrl = "https://healthsynq-kefa.onrender.com/generate-diet"; // change later

        try {
            ResponseEntity<Map> mlResponse =
                    restTemplate.postForEntity(mlUrl, requestBody, Map.class);

            if (!mlResponse.getStatusCode().is2xxSuccessful()) {
                throw new GenericBadRequestException("ML service failed");
            }

            Map<String, Object> mlData = mlResponse.getBody();
            Map<String, Object> cleaned = new HashMap<>();
            cleaned.put("summary", mlData.get("summary"));

            Map<String, Object> meals = new HashMap<>();
            meals.put("breakfast", extractFoodNames((List<Map<String, Object>>) mlData.get("breakfast")));
            meals.put("lunch", extractFoodNames((List<Map<String, Object>>) mlData.get("lunch")));
            meals.put("dinner", extractFoodNames((List<Map<String, Object>>) mlData.get("dinner")));
            meals.put("snack", extractFoodNames((List<Map<String, Object>>) mlData.get("snack")));

            cleaned.put("meals", meals);

            return new GenericResponse(
                    true,
                    "Diet generated successfully",
                    200,
                    cleaned
            );

        } catch (Exception e) {
            throw new GenericBadRequestException("Diet service unavailable");
        }
    }
    private List<String> extractFoodNames(List<Map<String, Object>> foods) {

        List<String> names = new ArrayList<>();

        if (foods == null) return names;

        for (Map<String, Object> item : foods) {
            Object name = item.get("food_name");
            if (name != null) {
                names.add(name.toString());
            }
        }

        return names;
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
}

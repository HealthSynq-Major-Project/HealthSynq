package com.health.HealthSynqBackend.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.health.HealthSynqBackend.dao.HealthDAO;
import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.PythonRegenerateDietRequest;
import com.health.HealthSynqBackend.dto.RegenerateDietAfterFeedbackRequest;
import com.health.HealthSynqBackend.entities.*;
import com.health.HealthSynqBackend.enums.DietStatus;
import com.health.HealthSynqBackend.enums.MealStatus;
import com.health.HealthSynqBackend.enums.MealType;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.core.type.TypeReference;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

@Service
public class DietServiceImpl implements DietService{
    private HealthDAO healthDAO;

    public DietServiceImpl(HealthDAO healthDAO){
        this.healthDAO = healthDAO;
    }

    @Override
    public GenericResponse generateDiet(int userId){
        try{
            Users user = validateUser(userId);

            UserDailyDiet existingDiet = checkExistingDiet(user);

            if(existingDiet != null){
                return buildExistingDietResponse(existingDiet);
            }

            UserCurrentHealth currentHealth = validateCurrentHealth(user);
            UserProfile profile = validateUserProfile(user);

            Integer glucose = getUserGlucose(user, currentHealth);

            UserWeeklyFoodHistory weeklyFoodHistory = getWeeklyFoodHistory(user);

            Map<String, Object> mlRequest = prepareGenerateDietRequest(currentHealth, glucose, weeklyFoodHistory);

            Map<String, Object> mlResponse = callGenerateDietAPI(mlRequest);

            UserDailyDiet dailyDiet = saveDailyDiet(user, currentHealth, mlResponse);

            saveDailyMeals(dailyDiet, mlResponse);

            updateWeeklyFoodHistory(user, weeklyFoodHistory, mlResponse);

            return buildGenerateDietResponse( dailyDiet,  mlResponse);
        }catch (GenericBadRequestException e){
            e.printStackTrace();
            throw e;
        }catch (Exception e){
            e.printStackTrace();
            throw new GenericBadRequestException("Unable to Generate Diet");
        }
    }

    private GenericResponse buildGenerateDietResponse(UserDailyDiet userDailyDiet,Map<String, Object> mlResponse) {
        GenericResponse response = new GenericResponse();

        Map<String,Object> responseData = new HashMap<>();

        responseData.put("dietId",userDailyDiet.getId());
        responseData.put("dietDate",userDailyDiet.getDietDate());
        responseData.put("dietPlan",mlResponse);

        response.setSuccess(true);
        response.setMessage("Diet generated successfully.");
        response.setStatusCode(200);
        response.setTimeStamp(System.currentTimeMillis());

        response.setData(responseData);
        return response;
    }

    private GenericResponse buildExistingDietResponse(UserDailyDiet dailyDiet) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();

            Map<String, Object> dietPlan = objectMapper.readValue(
                    dailyDiet.getCurrentPlanJson(),
                    new TypeReference<Map<String, Object>>() {}
            );

            Map<String, Object> responseData = new HashMap<>();

            responseData.put("dietId", dailyDiet.getId());
            responseData.put("dietDate", dailyDiet.getDietDate());
            responseData.put("status", dailyDiet.getStatus());
            responseData.put("dietPlan", dietPlan);

            GenericResponse response = new GenericResponse();

            response.setSuccess(true);
            response.setMessage("Today's diet already exists.");
            response.setStatusCode(200);
            response.setTimeStamp(System.currentTimeMillis());
            response.setData(responseData);

            return response;

        } catch (JsonProcessingException e) {
            throw new GenericBadRequestException("Unable to load existing diet.");
        }
    }

    @SuppressWarnings("unchecked")
    private void updateWeeklyFoodHistory(Users user, UserWeeklyFoodHistory weeklyHistory, Map<String, Object> mlResponse) throws JsonProcessingException{
        ObjectMapper mapper = new ObjectMapper();

        Map<String, List<List<String>>> weekUsed;

        if (weeklyHistory == null) {
            weeklyHistory = new UserWeeklyFoodHistory();
            weeklyHistory.setUser(user);
            LocalDate weekStart = getWeekStart(LocalDate.now());
            LocalDate weekEnd = getWeekEnd(LocalDate.now());

            weeklyHistory.setWeekStartDate(weekStart);
            weeklyHistory.setWeekEndDate(weekEnd);
            weekUsed = new HashMap<>();
        }else{
            if (weeklyHistory.getWeekUsedJson() == null || weeklyHistory.getWeekUsedJson().isBlank()) {
                weekUsed = new HashMap<>();
            } else {
                weekUsed = mapper.readValue( weeklyHistory.getWeekUsedJson(), new TypeReference<Map<String, List<List<String>>>>() {});
            }
        }
        processMeal("breakfast", mlResponse, weekUsed);
        processMeal("lunch", mlResponse, weekUsed);
        processMeal("snack", mlResponse, weekUsed);
        processMeal("dinner", mlResponse, weekUsed);
        weeklyHistory.setWeekUsedJson(mapper.writeValueAsString(weekUsed));
        weeklyHistory.setUpdatedAt(LocalDateTime.now());

        if (weeklyHistory.getCreatedAt() == null) {
            weeklyHistory.setCreatedAt(LocalDateTime.now());
            healthDAO.saveWeeklyFoodHistory(weeklyHistory);
        } else {
            healthDAO.updateWeeklyFoodHistory(weeklyHistory);
        }
    }

    @SuppressWarnings("unchecked")
    private void saveDailyMeals(UserDailyDiet userDailyDiet,Map<String, Object> mlResponse){
        Map<String, Object> summary = (Map<String,Object>) mlResponse.get("summary");
        Map<String, Object> mealKcal = (Map<String, Object>) summary.get("meal_kcal");

        createMeal(userDailyDiet, MealType.BREAKFAST, ((Number) mealKcal.get("breakfast")).doubleValue());

        createMeal(userDailyDiet, MealType.LUNCH, ((Number) mealKcal.get("lunch")).doubleValue());

        createMeal(userDailyDiet, MealType.SNACK, ((Number) mealKcal.get("snack")).doubleValue());

        createMeal(userDailyDiet, MealType.DINNER, ((Number) mealKcal.get("dinner")).doubleValue());
    }

    @SuppressWarnings("unchecked")
    private void processMeal(
            String mealName,
            Map<String, Object> mlResponse,
            Map<String, List<List<String>>> weekUsed) {

        List<Map<String, Object>> foods =
                (List<Map<String, Object>>) mlResponse.get(mealName);

        if (foods == null) {
            return;
        }

        for (Map<String, Object> food : foods) {

            String role = (String) food.get("food_role");
            String name = (String) food.get("food_name");
            String subCat = (String) food.get("food_subcat");

            addFood(role, name, subCat, weekUsed);
        }
    }

    private void addFood(
            String role,
            String name,
            String subCat,
            Map<String, List<List<String>>> weekUsed) {

        List<List<String>> foods =
                weekUsed.computeIfAbsent(role, k -> new ArrayList<>());

        for (List<String> item : foods) {

            if (item.get(0).equalsIgnoreCase(name)) {
                return;
            }
        }

        foods.add(Arrays.asList(name, subCat));
    }

    private void createMeal(
            UserDailyDiet dailyDiet,
            MealType mealType,
            Double plannedCalories) {

        UserDailyMeal meal = new UserDailyMeal();

        meal.setUserDailyDiet(dailyDiet);
        meal.setMealType(mealType);

        meal.setPlannedCalories(plannedCalories);
        meal.setConsumedCalories(0.0);
        meal.setRemainingCalories(plannedCalories);

        meal.setStatus(MealStatus.PLANNED);
        meal.setMealCompletedAt(null);

        meal.setCreatedAt(LocalDateTime.now());
        meal.setUpdatedAt(LocalDateTime.now());

        healthDAO.saveUserDailyMeal(meal);
    }

    private UserDailyDiet saveDailyDiet(Users user, UserCurrentHealth currentHealth, Map<String, Object> mlResponse) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();

            UserDailyDiet dailyDiet = new UserDailyDiet();
            dailyDiet.setUser(user);
            dailyDiet.setDietDate(LocalDate.now());

            dailyDiet.setConsumedCalories(0.0);
            dailyDiet.setTargetCalories(currentHealth.getDailyKcal().doubleValue());
            dailyDiet.setBurnedCalories(0.0);
            dailyDiet.setRemainingCalories(currentHealth.getDailyKcal().doubleValue());

            dailyDiet.setStatus(DietStatus.GENERATED);

            dailyDiet.setOriginalPlanJson(objectMapper.writeValueAsString(mlResponse));
            dailyDiet.setSummaryJson(objectMapper.writeValueAsString(mlResponse.get("summary")));
            dailyDiet.setCurrentPlanJson(objectMapper.writeValueAsString(mlResponse));

            dailyDiet.setCreatedAt(LocalDateTime.now());
            dailyDiet.setUpdatedAt(LocalDateTime.now());
            healthDAO.saveUserDailyDiet(dailyDiet);
            return dailyDiet;
        }catch (JsonProcessingException e){
            throw new GenericBadRequestException("Unable to save generated diet.");
        }
    }

    private Users validateUser(int userId){
        Users user = healthDAO.findUserById(userId);
        if (user == null) {
            throw new GenericBadRequestException("User not found");
        }
        return user;
    }
    private UserDailyDiet checkExistingDiet(Users user){
        return healthDAO.findTodayDiet(user);
    }
    private UserCurrentHealth validateCurrentHealth(Users user){
        UserCurrentHealth userCurrentHealth = healthDAO.findUser(user);
        if(userCurrentHealth == null){
            throw new GenericBadRequestException("Health data not available");
        }
        return userCurrentHealth;
    }

    private UserProfile validateUserProfile(Users user){
        UserProfile profile = healthDAO.findUserProfileByUser(user);

        if (profile == null) {
            throw new GenericBadRequestException("User profile not found");
        }
        return profile;
    }

    private Integer getUserGlucose(
            Users user,
            UserCurrentHealth currentHealth) {

        Integer glucose = currentHealth.getGlucoseLevel();

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
        return glucose;
    }

    private UserWeeklyFoodHistory getWeeklyFoodHistory(Users user){
        LocalDate weekStart = LocalDate.now().with(DayOfWeek.MONDAY);

        return healthDAO.findCurrentWeekHistory(user, weekStart);
    }

    private Map<String, Object> prepareGenerateDietRequest(UserCurrentHealth currentHealth, Integer glucose, UserWeeklyFoodHistory weeklyHistory) {
        Map<String, Object> request = new HashMap<>();
        request.put("glucose_mg_dl", glucose);
        request.put("daily_kcal", currentHealth.getDailyKcal());
        request.put("diet", currentHealth.getDietPreference());

        ObjectMapper mapper = new ObjectMapper();

        try {
            if (weeklyHistory != null && weeklyHistory.getWeekUsedJson() != null && !weeklyHistory.getWeekUsedJson().isBlank()) {
                request.put("week_used", mapper.readValue(
                                    weeklyHistory.getWeekUsedJson(),
                                    new TypeReference<Map<String, Object>>() {}
                        )
                );
            } else {
                request.put("week_used", new HashMap<>());
            }
        } catch (JsonProcessingException e) {
            throw new GenericBadRequestException("Unable to prepare diet request.");
        }
        return request;
    }

    private Map<String, Object> callGenerateDietAPI(
            Map<String, Object> request) {

        RestTemplate restTemplate = new RestTemplate();

        String mlUrl =
                "https://healthsynq-kefa.onrender.com/generate-diet";

        try {

            ResponseEntity<Map> response =
                    restTemplate.postForEntity(
                            mlUrl,
                            request,
                            Map.class
                    );

            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new GenericBadRequestException(
                        "ML service failed"
                );
            }

            return response.getBody();

        } catch (Exception e) {

            throw new GenericBadRequestException(
                    "Diet service unavailable"
            );
        }
    }

    private LocalDate getWeekStart(LocalDate date) {
        return date.with(DayOfWeek.MONDAY);
    }

    private LocalDate getWeekEnd(LocalDate date) {
        return date.with(DayOfWeek.SUNDAY);
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

//    Regenerate Diet after feedback
    @Override
    public GenericResponse regenerateDietAfterFeedback(int userId, RegenerateDietAfterFeedbackRequest request){
        try {
            Users user = validateUser(userId);
            UserDailyDiet dailyDiet = validateTodayDiet(user);
            Map<String, Object> currentDietPlan = getCurrentDietPlan(dailyDiet);
            UserWeeklyFoodHistory weeklyFoodHistory = getWeeklyFoodHistory(user);

            PythonRegenerateDietRequest pythonRequest = prepareRegenerateDietRequest(currentDietPlan, weeklyFoodHistory, request);

            Map<String, Object> mlResponse = callRegenerateDietAPI(pythonRequest);

            updateCurrentDiet(dailyDiet, mlResponse);

            replaceDailyMeals(dailyDiet, mlResponse);

            updateWeeklyFoodHistory(user, weeklyFoodHistory, mlResponse);

            return buildRegenerateDietResponse(dailyDiet, mlResponse);
        }catch (GenericBadRequestException e){
            e.printStackTrace();
            throw e;
        }
        catch (Exception e){
            e.printStackTrace();

            throw new GenericBadRequestException("Unable to regenerate diet.");
        }
    }

    private UserDailyDiet validateTodayDiet(Users user) {
        UserDailyDiet dailyDiet = healthDAO.findTodayDiet(user);

        if (dailyDiet == null) {
            throw new GenericBadRequestException(
                    "Today's diet not found. Generate diet first."
            );
        }
        return dailyDiet;
    }

    private Map<String, Object> getCurrentDietPlan(UserDailyDiet dailyDiet) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.readValue(dailyDiet.getCurrentPlanJson(), new TypeReference<Map<String, Object>>() {});
        } catch (Exception e) {
            throw new GenericBadRequestException("Unable to read current diet plan.");
        }
    }

    private PythonRegenerateDietRequest prepareRegenerateDietRequest(Map<String,Object> currentDietPlan, UserWeeklyFoodHistory weeklyFoodHistory, RegenerateDietAfterFeedbackRequest request){
        PythonRegenerateDietRequest pythonRequest = new PythonRegenerateDietRequest();

        pythonRequest.setOriginalPlan(currentDietPlan);

        pythonRequest.setActualIntake(request.getActualIntake());

        pythonRequest.setNotEaten(request.getNotEaten());

        pythonRequest.setCompletedSlots(request.getCompletedSlots());

        try {

            ObjectMapper objectMapper = new ObjectMapper();

            if (weeklyFoodHistory != null && weeklyFoodHistory.getWeekUsedJson() != null && !weeklyFoodHistory.getWeekUsedJson().isBlank()) {
                Map<String, Object> weekUsed = objectMapper.readValue(weeklyFoodHistory.getWeekUsedJson(), new TypeReference<Map<String, Object>>() {});
                pythonRequest.setWeekUsed(weekUsed);
            } else {
                pythonRequest.setWeekUsed(new HashMap<>());
            }

        } catch (Exception e) {
            throw new GenericBadRequestException("Unable to prepare regeneration request.");
        }

        return pythonRequest;
    }

    private Map<String, Object> callRegenerateDietAPI(PythonRegenerateDietRequest request){
        RestTemplate restTemplate = new RestTemplate();

        String mlUrl = "https://healthsynq-kefa.onrender.com/regenerate-diet-after-feedback";

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(mlUrl, request, Map.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new GenericBadRequestException("ML service failed");
            }
            return response.getBody();
        } catch (Exception e) {
            throw new GenericBadRequestException("Diet regeneration service unavailable");
        }
    }

    private void updateCurrentDiet(
            UserDailyDiet dailyDiet,
            Map<String, Object> mlResponse) {

        try {

            ObjectMapper objectMapper = new ObjectMapper();

            dailyDiet.setCurrentPlanJson(objectMapper.writeValueAsString(mlResponse));

            dailyDiet.setSummaryJson(objectMapper.writeValueAsString(mlResponse.get("summary")));

            dailyDiet.setUpdatedAt(LocalDateTime.now());
            healthDAO.updateUserDailyDiet(dailyDiet);

        } catch (JsonProcessingException e) {
            throw new GenericBadRequestException("Unable to update current diet.");
        }
    }

    @SuppressWarnings("unchecked")
    private void replaceDailyMeals(
            UserDailyDiet dailyDiet,
            Map<String, Object> mlResponse) {

        // Remove existing meals
        healthDAO.deleteDailyMeals(dailyDiet);

        // Read new meal calories
        Map<String, Object> summary =
                (Map<String, Object>) mlResponse.get("summary");

        Map<String, Object> mealKcal =
                (Map<String, Object>) summary.get("meal_kcal");

        // Create fresh meals
        createMeal(
                dailyDiet,
                MealType.BREAKFAST,
                ((Number) mealKcal.get("breakfast")).doubleValue()
        );

        createMeal(
                dailyDiet,
                MealType.LUNCH,
                ((Number) mealKcal.get("lunch")).doubleValue()
        );

        createMeal(
                dailyDiet,
                MealType.SNACK,
                ((Number) mealKcal.get("snack")).doubleValue()
        );

        createMeal(
                dailyDiet,
                MealType.DINNER,
                ((Number) mealKcal.get("dinner")).doubleValue()
        );
    }

    private GenericResponse buildRegenerateDietResponse(
            UserDailyDiet dailyDiet,
            Map<String, Object> mlResponse) {

        GenericResponse response = new GenericResponse();

        Map<String, Object> responseData = new HashMap<>();

        responseData.put("dietId", dailyDiet.getId());
        responseData.put("dietDate", dailyDiet.getDietDate());
        responseData.put("status", dailyDiet.getStatus());
        responseData.put("dietPlan", mlResponse);

        response.setSuccess(true);
        response.setMessage("Diet regenerated successfully.");
        response.setStatusCode(200);
        response.setTimeStamp(System.currentTimeMillis());
        response.setData(responseData);

        return response;
    }

}

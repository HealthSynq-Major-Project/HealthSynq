package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.*;
import com.health.HealthSynqBackend.enums.MealType;

import java.time.LocalDate;
import java.util.List;

public interface HealthDAO {
    public DailyHealthData findUserByIdAndDate(Users user, LocalDate date);
    public Users findUserById(int id);
    public void saveDailyHealthData(DailyHealthData data);
    public UserCurrentHealth findUser(Users user);
    public void saveUserCurrentHealth(UserCurrentHealth user);
    public UserProfile findUserProfileByUser(Users user);
    public UserGoal findGoalByUserId(int userId);
    UserGlucoseLog findLatestGlucose(Users user);
    void saveGlucoseLog(UserGlucoseLog userGlucoseLog);

    UserDailyDiet findTodayDiet(Users user);
    void saveUserDailyDiet(UserDailyDiet dailyDiet);
    void updateUserDailyDiet(UserDailyDiet dailyDiet);

    void saveUserDailyMeal(UserDailyMeal dailymeal);
    List<UserDailyMeal> findMealsByDailyDiet(UserDailyDiet dailyDiet);
    UserDailyMeal findMealByType(UserDailyDiet dailyDiet, MealType mealType);

    UserWeeklyFoodHistory findCurrentWeekHistory(Users user, LocalDate startWeekDate);
    void saveWeeklyFoodHistory(UserWeeklyFoodHistory history);
    void updateWeeklyFoodHistory(UserWeeklyFoodHistory history);
    void deleteDailyMeals(UserDailyDiet dailyDiet);

    List<UserGlucoseLog> findLastThreeGlucoseLogs(Users user);
}

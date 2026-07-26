package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.*;
import com.health.HealthSynqBackend.enums.MealType;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.transaction.Transactional;
import org.apache.catalina.User;
import org.apache.commons.lang3.reflect.Typed;
import org.springframework.stereotype.Repository;

import java.lang.reflect.Type;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.List;

@Repository
public class HealthDAOImpl implements HealthDAO{
    private EntityManager entityManager;
    public HealthDAOImpl(EntityManager entityManager){
        this.entityManager = entityManager;
    }

    @Override
    public DailyHealthData findUserByIdAndDate(Users user, LocalDate date) {
        TypedQuery<DailyHealthData> theQuery= entityManager.createQuery("from DailyHealthData d Where d.user = :user and d.date = :date",DailyHealthData.class);
        theQuery.setParameter("user",user);
        theQuery.setParameter("date",date);
        List<DailyHealthData> result = theQuery.getResultList();
        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    public Users findUserById(int id){
        TypedQuery<Users> query = entityManager.createQuery("from Users where id = :id",Users.class);

        query.setParameter("id",id);
        query.setMaxResults(1);

        List<Users> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public void saveDailyHealthData(DailyHealthData data){
        entityManager.merge(data);
    }

    @Override
    public UserCurrentHealth findUser(Users user){
        TypedQuery<UserCurrentHealth> query = entityManager.createQuery("from UserCurrentHealth where user = :user",UserCurrentHealth.class);

        query.setParameter("user",user);
        query.setMaxResults(1);

        List<UserCurrentHealth> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public void saveUserCurrentHealth(UserCurrentHealth theUser){
        entityManager.merge(theUser);
    }

    @Override
    public UserProfile findUserProfileByUser(Users user){
        TypedQuery<UserProfile> query = entityManager.createQuery("from UserProfile where user = :user",UserProfile.class);

        query.setParameter("user",user);
        query.setMaxResults(1);

        List<UserProfile> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public UserGoal findGoalByUserId(int userId){
        TypedQuery<UserGoal> query = entityManager.createQuery("FROM UserGoal g WHERE g.user.id = :userId",UserGoal.class);

        query.setParameter("userId",userId);
        query.setMaxResults(1);

        List<UserGoal> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public UserGlucoseLog findLatestGlucose(Users user){
        TypedQuery<UserGlucoseLog> theQuery = entityManager.createQuery("from UserGlucoseLog g Where g.users = :user Order By g.recordedAt DESC",UserGlucoseLog.class);

        theQuery.setParameter("user",user);
        theQuery.setMaxResults(1);
        List<UserGlucoseLog> result = theQuery.getResultList();

        return result.isEmpty()?null : result.get(0);
    }

    @Override
    public void saveGlucoseLog(UserGlucoseLog userGlucoseLog){
        entityManager.persist(userGlucoseLog);
    }


    @Override
    public UserDailyDiet findTodayDiet(Users user){
        LocalDate today = LocalDate.now();

        TypedQuery<UserDailyDiet> query = entityManager.createQuery("Select d from UserDailyDiet d Where d.user = :user and d.dietDate = :today",UserDailyDiet.class);

        query.setParameter("user",user);
        query.setParameter("today",today);

        List<UserDailyDiet> result = query.getResultList();
        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    @Transactional
    public void saveUserDailyDiet(UserDailyDiet dailyDiet) {
        entityManager.persist(dailyDiet);
    }

    @Override
    @Transactional
    public void updateUserDailyDiet(UserDailyDiet dailyDiet) {
        entityManager.merge(dailyDiet);
    }

    @Override
    @Transactional
    public void saveUserDailyMeal(UserDailyMeal meal) {
        entityManager.persist(meal);
    }

    @Override
    public List<UserDailyMeal> findMealsByDailyDiet(UserDailyDiet dailyDiet) {
        TypedQuery<UserDailyMeal> query =
                entityManager.createQuery(
                        "SELECT m FROM UserDailyMeal m " +
                                "WHERE m.userDailyDiet = :dailyDiet " +
                                "ORDER BY m.mealType",
                        UserDailyMeal.class
                );
        query.setParameter("dailyDiet", dailyDiet);
        return query.getResultList();
    }

    @Override
    public UserDailyMeal findMealByType(UserDailyDiet dailyDiet,
                                        MealType mealType) {
        TypedQuery<UserDailyMeal> query =
                entityManager.createQuery(
                        "SELECT m FROM UserDailyMeal m " +
                                "WHERE m.userDailyDiet = :dailyDiet " +
                                "AND m.mealType = :mealType",
                        UserDailyMeal.class
                );
        query.setParameter("dailyDiet", dailyDiet);
        query.setParameter("mealType", mealType);

        List<UserDailyMeal> result = query.getResultList();
        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    public UserWeeklyFoodHistory findCurrentWeekHistory(
            Users user,
            LocalDate weekStartDate) {

        TypedQuery<UserWeeklyFoodHistory> query =
                entityManager.createQuery(
                        "SELECT w FROM UserWeeklyFoodHistory w " +
                                "WHERE w.user = :user " +
                                "AND w.weekStartDate = :weekStart",
                        UserWeeklyFoodHistory.class
                );

        query.setParameter("user", user);
        query.setParameter("weekStart", weekStartDate);

        List<UserWeeklyFoodHistory> result = query.getResultList();

        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    @Transactional
    public void saveWeeklyFoodHistory(UserWeeklyFoodHistory history) {
        entityManager.persist(history);
    }

    @Override
    @Transactional
    public void updateWeeklyFoodHistory(UserWeeklyFoodHistory history) {
        entityManager.merge(history);
    }

    @Override
    @Transactional
    public void deleteDailyMeals(UserDailyDiet dailyDiet) {
        entityManager.createQuery(
                        "DELETE FROM UserDailyMeal m WHERE m.userDailyDiet = :diet")
                .setParameter("diet", dailyDiet)
                .executeUpdate();
    }

    @Override
    public List<UserGlucoseLog> findLastThreeGlucoseLogs(Users user) {

        return entityManager.createQuery(
                        "SELECT g FROM UserGlucoseLog g " +
                                "WHERE g.users = :user " +
                                "ORDER BY g.recordedAt DESC",
                        UserGlucoseLog.class)
                .setParameter("user", user)
                .setMaxResults(3)
                .getResultList();
    }


    // Helper Functions

    public LocalDate getWeekStart(LocalDate date){
        return date.with(DayOfWeek.MONDAY);
    }

    public LocalDate getWeekEnd(LocalDate date){
        return date.with(DayOfWeek.SUNDAY);
    }

}

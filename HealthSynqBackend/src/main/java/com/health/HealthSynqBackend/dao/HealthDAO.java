package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.*;

import java.time.LocalDate;

public interface HealthDAO {
    public DailyHealthData findUserByIdAndDate(Users user, LocalDate date);
    public Users findUserById(int id);
    public void saveDailyHealthData(DailyHealthData data);
    public UserCurrentHealth findUser(Users user);
    public void saveUserCurrentHealth(UserCurrentHealth user);
    public UserProfile findUserProfileByUser(Users user);
    public UserGoal findGoalByUserId(int userId);
}

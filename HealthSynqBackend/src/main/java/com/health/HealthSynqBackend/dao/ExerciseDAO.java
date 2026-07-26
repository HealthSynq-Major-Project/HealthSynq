package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.UserDailyWorkout;
import com.health.HealthSynqBackend.entities.Users;

public interface ExerciseDAO {
    UserDailyWorkout findTodayWorkout(Users user, String category);
    void saveUserDailyWorkout(UserDailyWorkout workout);
}

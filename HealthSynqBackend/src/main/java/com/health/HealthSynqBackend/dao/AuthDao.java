package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.UserGoal;
import com.health.HealthSynqBackend.entities.UserProfile;
import com.health.HealthSynqBackend.entities.Users;

public interface AuthDao {
    public boolean existByEmail(String email);
    public void saveUser(Users user);
    public void saveUserGoal(UserGoal userGoal);
    public void saveUserProfile(UserProfile userProfile);
    public boolean existByUserName(String userName);
    public Users findUser(String identifier);
}

package com.health.HealthSynqBackend.service;


import com.health.HealthSynqBackend.dto.LoginDTO;
import com.health.HealthSynqBackend.dto.AuthResponse;
import com.health.HealthSynqBackend.dto.UserDTO;
import com.health.HealthSynqBackend.dto.UserCheckDTO;

public interface AuthService {
    public AuthResponse saveUser(UserDTO theUser);
    public AuthResponse existUser(UserCheckDTO theUser);
    public AuthResponse loginUser(LoginDTO theUser);
}

package com.health.HealthSynqBackend.service;


import com.health.HealthSynqBackend.dto.LoginDTO;
import com.health.HealthSynqBackend.dto.LoginResponse;
import com.health.HealthSynqBackend.dto.SignupResponse;
import com.health.HealthSynqBackend.dto.UserDTO;
import com.health.HealthSynqBackend.dto.UserCheckDTO;

public interface AuthService {
    public SignupResponse saveUser(UserDTO theUser);
    public SignupResponse existUser(UserCheckDTO theUser);
    public LoginResponse loginUser(LoginDTO theUser);
}

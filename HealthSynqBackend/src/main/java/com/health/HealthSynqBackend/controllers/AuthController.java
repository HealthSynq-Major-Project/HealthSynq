package com.health.HealthSynqBackend.controllers;

import com.health.HealthSynqBackend.dto.LoginDTO;
import com.health.HealthSynqBackend.dto.LoginResponse;
import com.health.HealthSynqBackend.dto.SignupResponse;
import com.health.HealthSynqBackend.dto.UserDTO;
import com.health.HealthSynqBackend.dto.UserCheckDTO;
import com.health.HealthSynqBackend.service.AuthService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private AuthService authService;

    public AuthController(AuthService theAuthService){
        authService = theAuthService;
    }

    @PostMapping("/register")
    public SignupResponse registerUser(@RequestBody UserDTO theUser){
        System.out.println(theUser);
        return authService.saveUser(theUser);
    }
    @PostMapping("/check-user")
    public SignupResponse checkUser(@RequestBody UserCheckDTO theUser){
        return authService.existUser(theUser);
    }
    @PostMapping("/login")
    public LoginResponse loginUser(@RequestBody LoginDTO theUser){
        return authService.loginUser(theUser);
    }
}
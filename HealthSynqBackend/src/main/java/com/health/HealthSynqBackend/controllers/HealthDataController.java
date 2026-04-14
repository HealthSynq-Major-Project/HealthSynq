package com.health.HealthSynqBackend.controllers;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.HealthDTO;
import com.health.HealthSynqBackend.service.HealthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/health")
public class HealthDataController {
    private final HealthService healthService;

    public HealthDataController(HealthService healthService){
        this.healthService = healthService;
    }

    @PostMapping("/data")
    public ResponseEntity<GenericResponse> saveHealthData(HttpServletRequest request, @RequestBody HealthDTO health){
        int userId = (int) request.getAttribute("userId");

        GenericResponse response = healthService.processHealthData(userId,health);

        return ResponseEntity
                .status(response.getStatusCode())
                .body(response);
    }
}
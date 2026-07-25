package com.health.HealthSynqBackend.controllers;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.GlucoseDTO;
import com.health.HealthSynqBackend.dto.HealthDTO;
import com.health.HealthSynqBackend.service.HealthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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


    @PostMapping("/glucose")
    public ResponseEntity<GenericResponse> saveGlucoseLevels(HttpServletRequest request,  @RequestBody GlucoseDTO glucoseDTO){
        int userId = (int) request.getAttribute("userId");
        System.out.println(userId);
        System.out.println(glucoseDTO.getGlucose());

        GenericResponse response = healthService.updateGlucose(userId,glucoseDTO);

        return ResponseEntity.status(response.getStatusCode()).body(response);
    }

    @GetMapping("/data")
    public ResponseEntity<GenericResponse> getUserData(HttpServletRequest request){
        int userId = (int)request.getAttribute("userId");
        System.out.println(userId);
        GenericResponse response = healthService.getUserProfile(userId);
        return ResponseEntity.status(response.getStatusCode()).body(response);
    }

}
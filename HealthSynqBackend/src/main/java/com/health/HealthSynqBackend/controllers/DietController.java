package com.health.HealthSynqBackend.controllers;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.RegenerateDietAfterFeedbackRequest;
import com.health.HealthSynqBackend.service.DietService;
import com.health.HealthSynqBackend.service.DietServiceImpl;
import com.health.HealthSynqBackend.service.HealthService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/diet")
public class DietController {
    public DietService dietService;

    public DietController(DietService dietService){
        this.dietService = dietService;
    }
    @GetMapping("/today")
    public ResponseEntity<GenericResponse> getTodayDiet(HttpServletRequest request){
        int userId = (int) request.getAttribute("userId");

        GenericResponse response = dietService.generateDiet(userId);

        return ResponseEntity
                .status(response.getStatusCode())
                .body(response);
    }

    @PostMapping("/regenerate-after-feedback")
    public ResponseEntity<GenericResponse> regererateAfterFeedback(HttpServletRequest request, @RequestBody RegenerateDietAfterFeedbackRequest regenerateDietAfterFeedbackRequest){
        int userId = (int)request.getAttribute("userId");

        GenericResponse response = dietService.regenerateDietAfterFeedback(userId,regenerateDietAfterFeedbackRequest);
        return ResponseEntity.ok(response);
    }
}

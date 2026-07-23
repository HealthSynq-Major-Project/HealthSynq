package com.health.HealthSynqBackend.controllers;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.service.ExerciseService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/exercise")
public class ExerciseController {
    private ExerciseService exerciseService;
    public ExerciseController(ExerciseService exerciseService){
        this.exerciseService = exerciseService;
    }
    @GetMapping("/workout")
    public GenericResponse getWorkout(HttpServletRequest request, @RequestParam String category){
        int user_id = (int) request.getAttribute("userId");
        System.out.println(category);
        return exerciseService.getWorkout(category);
    }
}

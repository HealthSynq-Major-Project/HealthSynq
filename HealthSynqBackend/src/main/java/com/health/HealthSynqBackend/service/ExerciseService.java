package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dto.GenericResponse;
import org.springframework.stereotype.Service;


public interface ExerciseService {
    public GenericResponse getWorkout(int userId,String category);
}

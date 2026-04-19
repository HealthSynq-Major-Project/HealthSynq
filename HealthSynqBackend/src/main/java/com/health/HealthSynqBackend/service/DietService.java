package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dto.GenericResponse;

public interface DietService {
    GenericResponse generateDiet(int userId);
}

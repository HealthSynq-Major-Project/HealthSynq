package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.RegenerateDietAfterFeedbackRequest;

public interface DietService {
    GenericResponse generateDiet(int userId);
    GenericResponse regenerateDietAfterFeedback(int userId, RegenerateDietAfterFeedbackRequest request);
}

package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.dto.HealthDTO;

public interface HealthService {
    public GenericResponse processHealthData(int userId, HealthDTO healthDTO);
}

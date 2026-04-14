package com.health.HealthSynqBackend.exception;

public class GenericBadRequestException extends RuntimeException {
    public GenericBadRequestException(String message) {
        super(message);
    }
}

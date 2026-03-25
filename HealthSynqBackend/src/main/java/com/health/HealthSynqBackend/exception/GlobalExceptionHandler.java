package com.health.HealthSynqBackend.exception;

import com.health.HealthSynqBackend.dto.AuthResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<AuthResponse> handleAllExceptions(Exception ex) {
        ex.printStackTrace();

        AuthResponse response = new AuthResponse();
        response.setSuccess(false);
        response.setMessage("Internal Server Error: ");
        response.setStatusCode(500);
        response.setTimeStamp(System.currentTimeMillis());

        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    @ExceptionHandler(InvalidRequestException.class)
    public ResponseEntity<AuthResponse> handleInvalidRequest(InvalidRequestException e){
        AuthResponse response = new AuthResponse();
        response.setSuccess(false);
        response.setStatusCode(400);
        response.setMessage(e.getMessage());
        response.setTimeStamp(System.currentTimeMillis());
        response.setToken(null);
        response.setUserName(null);
        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(InvalidCredentialException.class)
    public ResponseEntity<AuthResponse> handleInvalidCredentials(InvalidCredentialException e){
        AuthResponse response = new AuthResponse();
        response.setSuccess(false);
        response.setStatusCode(401);
        response.setTimeStamp(System.currentTimeMillis());
        response.setMessage(e.getMessage());
        response.setToken(null);
        response.setUserName(null);
        return new ResponseEntity<>(response, HttpStatus.UNAUTHORIZED);
    }

    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<AuthResponse> userAlreadyExist(UserAlreadyExistsException e){
        AuthResponse response = new AuthResponse();
        response.setSuccess(false);
        response.setMessage(e.getMessage());
        response.setTimeStamp(System.currentTimeMillis());
        response.setStatusCode(409);
        response.setToken(null);
        response.setUserName(null);

        return new ResponseEntity<>(response,HttpStatus.CONFLICT);
    }
}

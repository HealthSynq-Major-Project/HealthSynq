package com.health.HealthSynqBackend.exception;

import com.health.HealthSynqBackend.dto.SignupResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<SignupResponse> handleAllExceptions(Exception ex) {
        ex.printStackTrace();

        SignupResponse response = new SignupResponse();
        response.setSuccess(false);
        response.setMessage("Internal Server Error: ");
        response.setStatusCode(500);
        response.setTimeStamp(System.currentTimeMillis());

        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    @ExceptionHandler(InvalidRequestException.class)
    public ResponseEntity<SignupResponse> handleInvalidRequest(InvalidRequestException e){
        SignupResponse signupResponse = new SignupResponse();
        signupResponse.setSuccess(false);
        signupResponse.setStatusCode(400);
        signupResponse.setMessage(e.getMessage());
        signupResponse.setTimeStamp(System.currentTimeMillis());
        return new ResponseEntity<>(signupResponse, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(InvalidCredentialException.class)
    public ResponseEntity<SignupResponse> handleInvalidCredentials(InvalidCredentialException e){
        SignupResponse response = new SignupResponse();
        response.setSuccess(false);
        response.setStatusCode(401);
        response.setTimeStamp(System.currentTimeMillis());
        response.setMessage(e.getMessage());
        return new ResponseEntity<>(response, HttpStatus.UNAUTHORIZED);
    }

    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<SignupResponse> userAlreadyExist(UserAlreadyExistsException e){
        SignupResponse signupResponse = new SignupResponse();
        signupResponse.setSuccess(false);
        signupResponse.setMessage(e.getMessage());
        signupResponse.setTimeStamp(System.currentTimeMillis());
        signupResponse.setStatusCode(409);
        return new ResponseEntity<>(signupResponse,HttpStatus.CONFLICT);
    }
}

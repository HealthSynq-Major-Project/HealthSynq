package com.health.HealthSynqBackend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class AuthResponse {
    private boolean success;
    private String message;
    private int statusCode;
    private long timeStamp;
    private String token;
    private String userName;

    public AuthResponse(){

    }

    public AuthResponse(boolean success, String message, int statusCode, long timeStamp, String token, String userName) {
        this.success = success;
        this.message = message;
        this.statusCode = statusCode;
        this.timeStamp = timeStamp;
        this.token = token;
        this.userName = userName;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public void setStatusCode(int statusCode) {
        this.statusCode = statusCode;
    }

    public long getTimeStamp() {
        return timeStamp;
    }

    public void setTimeStamp(long timeStamp) {
        this.timeStamp = timeStamp;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    @Override
    public String toString() {
        return "SignupResponse{" +
                "success=" + success +
                ", message='" + message + '\'' +
                ", statusCode=" + statusCode +
                ", timeStamp=" + timeStamp +
                '}';
    }
}

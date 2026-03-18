package com.health.HealthSynqBackend.dto;

public class SignupResponse {
    private boolean success;
    private String message;
    private int statusCode;
    private long timeStamp;

    public SignupResponse(){

    }

    public SignupResponse(boolean success, String message, int statusCode, long timeStamp) {
        this.success = success;
        this.message = message;
        this.statusCode = statusCode;
        this.timeStamp = timeStamp;
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

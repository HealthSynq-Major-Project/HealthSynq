package com.health.HealthSynqBackend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class GenericResponse {
    private boolean success;
    private String message;
    private int statusCode;
    private long timeStamp;
    private Object data;

    public GenericResponse() {}

    public GenericResponse(boolean success, String message, int statusCode, Object data) {
        this.success = success;
        this.message = message;
        this.statusCode = statusCode;
        this.timeStamp = System.currentTimeMillis();
        this.data = data;
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

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}

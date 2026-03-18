package com.health.HealthSynqBackend.dto;

public class UserCheckDTO {
    private String email;
    private String userName;

    public UserCheckDTO() {}

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }
}

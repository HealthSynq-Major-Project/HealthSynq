package com.health.HealthSynqBackend.dto;

public class UserDTO {
    private String email;
    private String userName;
    private String password;
    private Integer age;
    private String gender;
    private Integer weight;
    private String weightType;
    private Integer height;
    private String heightType;
    private Integer targetWeight;
    private String targetWeightType;
    private Integer targetDurationDays;
    private Boolean isDiabetic;


    public UserDTO(String email, String userName, String password, Integer age, String gender, Integer weight, String weightType, Integer height, String heightType, Integer targetWeight, String targetWeightType, Integer targetDurationDays, Boolean isDiabetic) {
        this.email = email;
        this.userName = userName;
        this.password = password;
        this.age = age;
        this.gender = gender;
        this.weight = weight;
        this.weightType = weightType;
        this.height = height;
        this.heightType = heightType;
        this.targetWeight = targetWeight;
        this.targetWeightType = targetWeightType;
        this.targetDurationDays = targetDurationDays;
        this.isDiabetic = isDiabetic;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public Boolean getDiabetic() {
        return isDiabetic;
    }

    public void setDiabetic(Boolean diabetic) {
        isDiabetic = diabetic;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public Integer getWeight() {
        return weight;
    }

    public void setWeight(Integer weight) {
        this.weight = weight;
    }

    public String getWeightType() {
        return weightType;
    }

    public void setWeightType(String weightType) {
        this.weightType = weightType;
    }

    public Integer getHeight() {
        return height;
    }

    public void setHeight(Integer height) {
        this.height = height;
    }

    public String getHeightType() {
        return heightType;
    }

    public void setHeightType(String heightType) {
        this.heightType = heightType;
    }

    public Integer getTargetWeight() {
        return targetWeight;
    }

    public void setTargetWeight(Integer targetWeight) {
        this.targetWeight = targetWeight;
    }

    public String getTargetWeightType() {
        return targetWeightType;
    }

    public void setTargetWeightType(String targetWeightType) {
        this.targetWeightType = targetWeightType;
    }

    public Integer getTargetDurationDays() {
        return targetDurationDays;
    }

    public void setTargetDurationDays(Integer targetDurationDays) {
        this.targetDurationDays = targetDurationDays;
    }

    public Boolean getIsDiabetic() {
        return isDiabetic;
    }

    public void setIsDiabetic(Boolean diabetic) {
        isDiabetic = diabetic;
    }

    @Override
    public String toString() {
        return "UserDTO{" +
                "email='" + email + '\'' +
                ", userName='" + userName + '\'' +
                ", password='" + password + '\'' +
                ", age=" + age +
                ", gender='" + gender + '\'' +
                ", weight=" + weight +
                ", weightType='" + weightType + '\'' +
                ", height=" + height +
                ", heightType='" + heightType + '\'' +
                ", targetWeight=" + targetWeight +
                ", targetWeightType='" + targetWeightType + '\'' +
                ", targetDurationDays=" + targetDurationDays +
                ", isDiabetic=" + isDiabetic +
                '}';
    }
}

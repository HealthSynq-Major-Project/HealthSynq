package com.health.HealthSynqBackend.dto;

public class HealthDTO {
    private Integer steps;
    private Integer heartRateAvg;
    private Double caloriesBurned;
    private Double sleepHours;
    private Double spO2;

    public HealthDTO(){

    }

    public HealthDTO(Integer steps, Integer heartRateAvg, Double caloriesBurned, Double sleepHours, Double spO2) {
        this.steps = steps;
        this.heartRateAvg = heartRateAvg;
        this.caloriesBurned = caloriesBurned;
        this.sleepHours = sleepHours;
        this.spO2 = spO2;
    }

    public Integer getSteps() {
        return steps;
    }

    public void setSteps(Integer steps) {
        this.steps = steps;
    }

    public Integer getHeartRateAvg() {
        return heartRateAvg;
    }

    public void setHeartRateAvg(Integer heartRateAvg) {
        this.heartRateAvg = heartRateAvg;
    }

    public Double getCaloriesBurned() {
        return caloriesBurned;
    }

    public void setCaloriesBurned(Double caloriesBurned) {
        this.caloriesBurned = caloriesBurned;
    }

    public Double getSleepHours() {
        return sleepHours;
    }

    public void setSleepHours(Double sleepHours) {
        this.sleepHours = sleepHours;
    }

    public Double getSpO2() {
        return spO2;
    }

    public void setSpO2(Double spO2) {
        this.spO2 = spO2;
    }
}

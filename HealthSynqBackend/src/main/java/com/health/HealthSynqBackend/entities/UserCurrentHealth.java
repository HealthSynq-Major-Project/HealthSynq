package com.health.HealthSynqBackend.entities;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "user_current_health",
        uniqueConstraints = @UniqueConstraint(columnNames = "user_id")
)
public class UserCurrentHealth {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private Users user;

    private Integer steps;
    private Integer heartRateAvg;
    private Double caloriesBurned;
    private Double sleepHours;
    private Double spO2;

    private Integer glucoseLevel; // nullable

    @Column(nullable = false)
    private String dietPreference = "veg"; // default

    private Integer dailyKcal;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public UserCurrentHealth() {}

    public UserCurrentHealth(Users user) {
        this.user = user;
        this.dietPreference = "veg";
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Users getUser() {
        return user;
    }

    public void setUser(Users user) {
        this.user = user;
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

    public Integer getGlucoseLevel() {
        return glucoseLevel;
    }

    public void setGlucoseLevel(Integer glucoseLevel) {
        this.glucoseLevel = glucoseLevel;
    }

    public Integer getDailyKcal() {
        return dailyKcal;
    }

    public void setDailyKcal(Integer dailyKcal) {
        this.dailyKcal = dailyKcal;
    }

    public String getDietPreference() {
        return dietPreference;
    }

    public void setDietPreference(String dietPreference) {
        this.dietPreference = dietPreference;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "UserCurrentHealth{" +
                "id=" + id +
                ", user=" + user +
                ", steps=" + steps +
                ", heartRateAvg=" + heartRateAvg +
                ", caloriesBurned=" + caloriesBurned +
                ", sleepHours=" + sleepHours +
                ", spO2=" + spO2 +
                ", glucoseLevel=" + glucoseLevel +
                ", dietPreference='" + dietPreference + '\'' +
                ", dailyKcal=" + dailyKcal +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
}

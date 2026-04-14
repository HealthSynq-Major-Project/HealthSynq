package com.health.HealthSynqBackend.entities;

import jakarta.persistence.*;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "daily_health_data",
        uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "date"})
)
public class DailyHealthData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private Users user;

    @Column(nullable = false)
    private LocalDate date; // Used for grouping

    private Integer steps;

    private Integer heartRateAvg;

    private Double caloriesBurned;

    private Double sleepHours;

    private Double spO2;

    private LocalDateTime createdAt;    // For timestamp

    private LocalDateTime updatedAt;    // For timestamp

    public DailyHealthData(){

    }

    public DailyHealthData(Users user, LocalDate date, Integer steps, Integer heartRateAvg, Double caloriesBurned, Double sleepHours, Double spO2) {
        this.user = user;
        this.date = date;
        this.steps = steps;
        this.heartRateAvg = heartRateAvg;
        this.caloriesBurned = caloriesBurned;
        this.sleepHours = sleepHours;
        this.spO2 = spO2;
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

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
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

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    @Override
    public String toString() {
        return "DailyHealthData{" +
                "id=" + id +
                ", user=" + user +
                ", date=" + date +
                ", steps=" + steps +
                ", heartRateAvg=" + heartRateAvg +
                ", caloriesBurned=" + caloriesBurned +
                ", sleepHours=" + sleepHours +
                ", spO2=" + spO2 +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
}

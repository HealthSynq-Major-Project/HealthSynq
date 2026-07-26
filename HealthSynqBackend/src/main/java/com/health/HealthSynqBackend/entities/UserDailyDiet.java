package com.health.HealthSynqBackend.entities;

import com.health.HealthSynqBackend.enums.DietStatus;
import jakarta.persistence.*;
import org.apache.catalina.User;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name="user_daily_diet", uniqueConstraints = {@UniqueConstraint(columnNames = {"user_id","diet_date"})})
public class UserDailyDiet {
    @Id
    @GeneratedValue(strategy =  GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name="user_id", nullable = false)
    private Users user;

    @Column(name="diet_date", nullable = false)
    private LocalDate dietDate;

    @Column(name="target_calories",nullable = false)
    private Double targetCalories;

    @Column(name = "consumed_calories", nullable = false)
    private Double consumedCalories = 0.0;

    @Column(name = "burned_calories", nullable = false)
    private Double burnedCalories = 0.0;

    @Column(name = "remaining_calories", nullable = false)
    private Double remainingCalories;

    @Column(name = "original_plan", columnDefinition = "TEXT")
    private String originalPlanJson;

    @Column(name = "current_plan", columnDefinition = "TEXT")
    private String currentPlanJson;

    @Column(name = "summary", columnDefinition = "TEXT")
    private String summaryJson;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DietStatus status = DietStatus.GENERATED;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;



    public UserDailyDiet() {
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Users getUser() {
        return user;
    }

    public void setUser(Users user) {
        this.user = user;
    }

    public LocalDate getDietDate() {
        return dietDate;
    }

    public void setDietDate(LocalDate dietDate) {
        this.dietDate = dietDate;
    }

    public Double getConsumedCalories() {
        return consumedCalories;
    }

    public void setConsumedCalories(Double consumedCalories) {
        this.consumedCalories = consumedCalories;
    }

    public Double getTargetCalories() {
        return targetCalories;
    }

    public void setTargetCalories(Double targetCalories) {
        this.targetCalories = targetCalories;
    }

    public Double getBurnedCalories() {
        return burnedCalories;
    }

    public void setBurnedCalories(Double burnedCalories) {
        this.burnedCalories = burnedCalories;
    }

    public Double getRemainingCalories() {
        return remainingCalories;
    }

    public void setRemainingCalories(Double remainingCalories) {
        this.remainingCalories = remainingCalories;
    }

    public String getOriginalPlanJson() {
        return originalPlanJson;
    }

    public void setOriginalPlanJson(String originalPlanJson) {
        this.originalPlanJson = originalPlanJson;
    }

    public String getCurrentPlanJson() {
        return currentPlanJson;
    }

    public void setCurrentPlanJson(String currentPlanJson) {
        this.currentPlanJson = currentPlanJson;
    }

    public String getSummaryJson() {
        return summaryJson;
    }

    public void setSummaryJson(String summaryJson) {
        this.summaryJson = summaryJson;
    }

    public DietStatus getStatus() {
        return status;
    }

    public void setStatus(DietStatus status) {
        this.status = status;
    }

    @PrePersist
    public void prePersist() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void preUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

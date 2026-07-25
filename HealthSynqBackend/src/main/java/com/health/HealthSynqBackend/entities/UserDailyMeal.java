package com.health.HealthSynqBackend.entities;

import com.health.HealthSynqBackend.enums.MealStatus;
import com.health.HealthSynqBackend.enums.MealType;
import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name="user_daily_meal",uniqueConstraints = {@UniqueConstraint(columnNames = {"daily_diet_id", "meal_type"})})
public class UserDailyMeal {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "daily_diet_id", nullable = false)
    private UserDailyDiet userDailyDiet;

    @Enumerated(EnumType.STRING)
    @Column(name = "meal_type", nullable = false)
    private MealType mealType;

    @Column(name = "planned_calories", nullable = false)
    private Double plannedCalories;

    @Column(name = "consumed_calories", nullable = false)
    private Double consumedCalories = 0.0;

    @Column(name = "remaining_calories", nullable = false)
    private Double remainingCalories;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private MealStatus status = MealStatus.PLANNED;

    @Column(name = "meal_completed_at")
    private LocalDateTime mealCompletedAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public UserDailyMeal() {

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

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public UserDailyDiet getUserDailyDiet() {
        return userDailyDiet;
    }

    public void setUserDailyDiet(UserDailyDiet userDailyDiet) {
        this.userDailyDiet = userDailyDiet;
    }

    public MealType getMealType() {
        return mealType;
    }

    public void setMealType(MealType mealType) {
        this.mealType = mealType;
    }

    public Double getPlannedCalories() {
        return plannedCalories;
    }

    public void setPlannedCalories(Double plannedCalories) {
        this.plannedCalories = plannedCalories;
    }

    public Double getConsumedCalories() {
        return consumedCalories;
    }

    public void setConsumedCalories(Double consumedCalories) {
        this.consumedCalories = consumedCalories;
    }

    public MealStatus getStatus() {
        return status;
    }

    public void setStatus(MealStatus status) {
        this.status = status;
    }

    public LocalDateTime getMealCompletedAt() {
        return mealCompletedAt;
    }

    public void setMealCompletedAt(LocalDateTime mealCompletedAt) {
        this.mealCompletedAt = mealCompletedAt;
    }

    public Double getRemainingCalories() {
        return remainingCalories;
    }

    public void setRemainingCalories(Double remainingCalories) {
        this.remainingCalories = remainingCalories;
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

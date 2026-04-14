package com.health.HealthSynqBackend.entities;

import jakarta.persistence.*;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name="user_goal")
public class UserGoal {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name="id")
    private int id;

    @Column(name="target_weight_grams")
    private long targetWeight;

    @Column(name="target_duration_days")
    private int targetDuration;

    @Column(name="start_date")
    private LocalDateTime startDate;

    @Column(name="created_at")
    private LocalDateTime createdAt;

    @ManyToOne
    @JoinColumn(name="user_id",nullable = false)
    private Users user;

    public UserGoal() {
    }

    public UserGoal(long targetWeight, int targetDuration, LocalDateTime startDate, LocalDateTime createdAt) {
        this.targetWeight = targetWeight;
        this.targetDuration = targetDuration;
        this.createdAt = createdAt;
        this.startDate = startDate;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public long getTargetWeight() {
        return targetWeight;
    }

    public void setTargetWeight(long targetWeight) {
        this.targetWeight = targetWeight;
    }

    public int getTargetDuration() {
        return targetDuration;
    }

    public void setTargetDuration(int targetDuration) {
        this.targetDuration = targetDuration;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public Users getUser() {
        return user;
    }

    public void setUser(Users user) {
        this.user = user;
    }

    public LocalDateTime getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDateTime startDate) {
        this.startDate = startDate;
    }

    @Override
    public String toString() {
        return "UserGoal{" +
                "id=" + id +
                ", targetWeight=" + targetWeight +
                ", targetDuration=" + targetDuration +
                ", startDate=" + startDate +
                ", createdAt=" + createdAt +
                ", user=" + user +
                '}';
    }
}

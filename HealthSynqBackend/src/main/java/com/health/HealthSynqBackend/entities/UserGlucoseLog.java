package com.health.HealthSynqBackend.entities;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "user_glucose_logs")
public class UserGlucoseLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name="user_id",nullable = false)
    private Users users;

    @Column(name="glucose_level",nullable = false)
    private Integer glucoseLevel;

    @Column(name="recorded_at",nullable = false)
    private LocalDateTime recordedAt;

    @Column(name="created_at")
    private LocalDateTime createdAt;

    public UserGlucoseLog(){

    }

    public UserGlucoseLog(Users users, Integer glucoseLevel, LocalDateTime recordedAt) {
        this.users = users;
        this.glucoseLevel = glucoseLevel;
        this.recordedAt = recordedAt;
    }

    public Users getUsers() {
        return users;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setUsers(Users users) {
        this.users = users;
    }

    public Integer getGlucoseLevel() {
        return glucoseLevel;
    }

    public void setGlucoseLevel(Integer glucoseLevel) {
        this.glucoseLevel = glucoseLevel;
    }

    public LocalDateTime getRecordedAt() {
        return recordedAt;
    }

    public void setRecordedAt(LocalDateTime recordedAt) {
        this.recordedAt = recordedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "UserGlucoseLog{" +
                "id=" + id +
                ", users=" + users +
                ", glucoseLevel=" + glucoseLevel +
                ", recordedAt=" + recordedAt +
                ", createdAt=" + createdAt +
                '}';
    }
}

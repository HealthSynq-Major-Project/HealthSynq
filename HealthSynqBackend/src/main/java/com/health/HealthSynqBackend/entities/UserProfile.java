package com.health.HealthSynqBackend.entities;

import jakarta.persistence.*;

@Entity
public class UserProfile {
    @Id
    @Column(name="id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    @Column(name="age")
    private int age;

    @Column(name="gender")
    private String gender;

    @Column(name="height_cm")
    private int height;

    @Column(name="weight_grams")
    private long weight;

    @Column(name="is_diabetic")
    private boolean isDiabetic;

    @Column(name="bmi")
    private Double bmi;

    @OneToOne
    @JoinColumn(name="user_id",nullable = false,unique=true)
    private Users user;

    public UserProfile() {
    }

    public UserProfile(int age, String gender, int height, long weight, boolean isDiabetic, Double bmi) {
        this.age = age;
        this.gender = gender;
        this.height = height;
        this.weight = weight;
        this.isDiabetic = isDiabetic;
        this.bmi = bmi;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public int getHeight() {
        return height;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public long getWeight() {
        return weight;
    }

    public void setWeight(long weight) {
        this.weight = weight;
    }

    public boolean isDiabetic() {
        return isDiabetic;
    }

    public void setDiabetic(boolean diabetic) {
        isDiabetic = diabetic;
    }

    public Double getBmi() {
        return bmi;
    }

    public void setBmi(Double bmi) {
        this.bmi = bmi;
    }

    public Users getUser() {
        return user;
    }

    public void setUser(Users user) {
        this.user = user;
    }

    @Override
    public String toString() {
        return "UserProfile{" +
                "bmi=" + bmi +
                ", isDiabetic=" + isDiabetic +
                ", weight=" + weight +
                ", height=" + height +
                ", gender='" + gender + '\'' +
                ", age=" + age +
                ", id=" + id +
                '}';
    }
}

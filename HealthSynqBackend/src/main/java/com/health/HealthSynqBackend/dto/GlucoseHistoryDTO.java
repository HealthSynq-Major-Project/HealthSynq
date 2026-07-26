package com.health.HealthSynqBackend.dto;

import java.time.LocalDateTime;

public class GlucoseHistoryDTO {
    private Integer glucose;
    private String unit;
    private String readingType;
    private LocalDateTime recordedAt;

    public GlucoseHistoryDTO() {
    }

    public GlucoseHistoryDTO(Integer glucose, String unit, String readingType, LocalDateTime recordedAt) {
        this.glucose = glucose;
        this.unit = unit;
        this.readingType = readingType;
        this.recordedAt = recordedAt;
    }

    public Integer getGlucose() {
        return glucose;
    }

    public void setGlucose(Integer glucose) {
        this.glucose = glucose;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public String getReadingType() {
        return readingType;
    }

    public void setReadingType(String readingType) {
        this.readingType = readingType;
    }

    public LocalDateTime getRecordedAt() {
        return recordedAt;
    }

    public void setRecordedAt(LocalDateTime recordedAt) {
        this.recordedAt = recordedAt;
    }
}

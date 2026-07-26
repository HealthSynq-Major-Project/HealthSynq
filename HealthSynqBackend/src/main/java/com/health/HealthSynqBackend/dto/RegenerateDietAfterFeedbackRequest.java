package com.health.HealthSynqBackend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class RegenerateDietAfterFeedbackRequest {

    @JsonProperty("actual_intake")
    private Map<String, Object> actualIntake;

    @JsonProperty("not_eaten")
    private Map<String, List<String>> notEaten;

    @JsonProperty("completed_slots")
    private List<String> completedSlots;

    @JsonProperty("week_used")
    private Map<String, Object> weekUsed;

    public RegenerateDietAfterFeedbackRequest() {
    }

    public Map<String, Object> getActualIntake() {
        return actualIntake;
    }

    public void setActualIntake(Map<String, Object> actualIntake) {
        this.actualIntake = actualIntake;
    }

    public Map<String, List<String>> getNotEaten() {
        return notEaten;
    }

    public void setNotEaten(Map<String, List<String>> notEaten) {
        this.notEaten = notEaten;
    }

    public List<String> getCompletedSlots() {
        return completedSlots;
    }

    public void setCompletedSlots(List<String> completedSlots) {
        this.completedSlots = completedSlots;
    }

    public Map<String, Object> getWeekUsed() {
        return weekUsed;
    }

    public void setWeekUsed(Map<String, Object> weekUsed) {
        this.weekUsed = weekUsed;
    }
}

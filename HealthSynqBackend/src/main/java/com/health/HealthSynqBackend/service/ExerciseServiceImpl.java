package com.health.HealthSynqBackend.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.health.HealthSynqBackend.dao.ExerciseDAO;
import com.health.HealthSynqBackend.dao.ExerciseDAOImpl;
import com.health.HealthSynqBackend.dao.HealthDAO;
import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.entities.UserDailyWorkout;
import com.health.HealthSynqBackend.entities.Users;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.FileCopyUtils;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ExerciseServiceImpl implements ExerciseService{
    private HealthDAO healthDAO;
    private ExerciseDAO exerciseDAO;
    public ExerciseServiceImpl(HealthDAO healthDAO, ExerciseDAO exerciseDAO){
        this.healthDAO = healthDAO;
        this.exerciseDAO = exerciseDAO;
    }
    @Override
    public GenericResponse getWorkout(int userId, String category) {
        Users user = healthDAO.findUserById(userId);
        if (user == null) {
            throw new GenericBadRequestException("User not found");
        }
        try {
            UserDailyWorkout dailyWorkout = exerciseDAO.findTodayWorkout(user, category);
            List<Map<String, Object>> exercises;
            ObjectMapper mapper = new ObjectMapper();

            if (dailyWorkout != null) {
                exercises = mapper.readValue(
                        dailyWorkout.getWorkoutJson(),
                        new TypeReference<List<Map<String, Object>>>() {}
                );
            } else {
                Map<String, Object> requestBody = new HashMap<>();
                requestBody.put("category", category);
                RestTemplate restTemplate = new RestTemplate();
                String url = "https://healthsynq-kefa.onrender.com/generate-workout";

                ResponseEntity<Map> response =
                        restTemplate.postForEntity(
                                url,
                                requestBody,
                                Map.class
                        );

                if (!response.getStatusCode().is2xxSuccessful()) {
                    throw new GenericBadRequestException("ML service failed");
                }

                Map<String, Object> responseBody = response.getBody();
                Boolean success = (Boolean) responseBody.get("success");

                if (Boolean.FALSE.equals(success)) {
                    throw new GenericBadRequestException("Category not defined");
                }

                exercises = (List<Map<String, Object>>) responseBody.get("workout");

                UserDailyWorkout workout = new UserDailyWorkout();

                workout.setUser(user);
                workout.setCategory(category);
                workout.setWorkoutDate(LocalDate.now());

                workout.setWorkoutJson(mapper.writeValueAsString(exercises));

                workout.setCreatedAt(LocalDateTime.now());
                workout.setUpdatedAt(LocalDateTime.now());

                exerciseDAO.saveUserDailyWorkout(workout);
            }

            for (Map<String, Object> exercise : exercises) {
                String gifPath = (String) exercise.get("gif_url");

                ClassPathResource resource = new ClassPathResource("static/" + gifPath);

                byte[] bytes = FileCopyUtils.copyToByteArray(resource.getInputStream());

                String base64Gif = Base64.getEncoder().encodeToString(bytes);

                exercise.put("gif", base64Gif);
                exercise.remove("gif_url");
            }

            return new GenericResponse(
                    true,
                    "Workout generated successfully",
                    200,
                    exercises
            );

        } catch (Exception e) {
            e.printStackTrace();
            throw new GenericBadRequestException("Exercise service unavailable");
        }
    }
}

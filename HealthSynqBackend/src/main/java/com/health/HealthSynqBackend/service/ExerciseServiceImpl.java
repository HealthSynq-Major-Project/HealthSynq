package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dto.GenericResponse;
import com.health.HealthSynqBackend.exception.GenericBadRequestException;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.FileCopyUtils;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.client.RestTemplate;

import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ExerciseServiceImpl implements ExerciseService{
    @Override
    public GenericResponse getWorkout(String category){
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("category",category);
        RestTemplate restTemplate = new RestTemplate();
        String url = "https://healthsynq-kefa.onrender.com/generate-workout";


        try{
            ResponseEntity<Map> response = restTemplate.postForEntity(url,requestBody,Map.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new GenericBadRequestException("ML service failed");
            }


            Map<String,Object> responseBody = response.getBody();

            Boolean success = (Boolean) responseBody.get("success");
            if(Boolean.FALSE.equals(success)){
                throw new GenericBadRequestException("Category not defined");
            }


            List<Map<String, Object>> exercises =(List<Map<String, Object>>) responseBody.get("workout");

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
            throw new GenericBadRequestException("Exercise service unavailable");
        }

    }
}

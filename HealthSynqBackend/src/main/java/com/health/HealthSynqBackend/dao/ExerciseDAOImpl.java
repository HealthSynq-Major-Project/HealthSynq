package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.UserDailyWorkout;
import com.health.HealthSynqBackend.entities.Users;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public class ExerciseDAOImpl implements ExerciseDAO{
    private EntityManager entityManager;
    public ExerciseDAOImpl(EntityManager entityManager){
        this.entityManager = entityManager;
    }
    @Override
    public UserDailyWorkout findTodayWorkout(Users user, String category){
        TypedQuery<UserDailyWorkout> query =
                entityManager.createQuery(
                        "SELECT w FROM UserDailyWorkout w " +
                                "WHERE w.user = :user " +
                                "AND w.category = :category " +
                                "AND w.workoutDate = :today",
                        UserDailyWorkout.class
                );

        query.setParameter("user", user);
        query.setParameter("category", category);
        query.setParameter("today", LocalDate.now());

        List<UserDailyWorkout> result = query.getResultList();
        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    @Transactional
    public void saveUserDailyWorkout(UserDailyWorkout workout) {
        entityManager.persist(workout);
    }
}

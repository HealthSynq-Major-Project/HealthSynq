package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.UserGoal;
import com.health.HealthSynqBackend.entities.UserProfile;
import com.health.HealthSynqBackend.entities.Users;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class AuthDaoImpl implements AuthDao{
    private EntityManager entityManager;

    public AuthDaoImpl(EntityManager theEntityManager){
        entityManager = theEntityManager;
    }

    public boolean existByEmail(String email){
        TypedQuery<Users> typedQuery = entityManager.createQuery("from Users where email = :email",Users.class);
        typedQuery.setParameter("email",email);

        List<Users> theList = typedQuery.getResultList();
        return !theList.isEmpty();
    }

    public void saveUser(Users user){
        entityManager.persist(user);
    }

    public void saveUserGoal(UserGoal userGoal){
        entityManager.persist(userGoal);
    }

    public void saveUserProfile(UserProfile userProfile){
        entityManager.persist(userProfile);
    }

    @Override
    public boolean existByUserName(String userName) {
        TypedQuery<Users> query = entityManager.createQuery(
                "from Users where userName = :userName",
                Users.class
        );

        query.setParameter("userName", userName);

        List<Users> result = query.getResultList();

        return !result.isEmpty();
    }

    @Override
    public Users findUser(String identifier){
        TypedQuery<Users> query = entityManager.createQuery(
                "from Users where email = :identifier OR userName = :identifier",
                Users.class
        );

        query.setParameter("identifier", identifier);
        query.setMaxResults(1);

        List<Users> result = query.getResultList();

        return result.isEmpty() ? null : result.get(0);
    } 
}

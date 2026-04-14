package com.health.HealthSynqBackend.dao;

import com.health.HealthSynqBackend.entities.*;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import org.apache.catalina.User;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public class HealthDAOImpl implements HealthDAO{
    private EntityManager entityManager;
    public HealthDAOImpl(EntityManager entityManager){
        this.entityManager = entityManager;
    }

    @Override
    public DailyHealthData findUserByIdAndDate(Users user, LocalDate date) {
        TypedQuery<DailyHealthData> theQuery= entityManager.createQuery("from DailyHealthData d Where d.user = :user and d.date = :date",DailyHealthData.class);
        theQuery.setParameter("user",user);
        theQuery.setParameter("date",date);
        List<DailyHealthData> result = theQuery.getResultList();
        return result.isEmpty() ? null : result.get(0);
    }

    @Override
    public Users findUserById(int id){
        TypedQuery<Users> query = entityManager.createQuery("from Users where id = :id",Users.class);

        query.setParameter("id",id);
        query.setMaxResults(1);

        List<Users> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public void saveDailyHealthData(DailyHealthData data){
        entityManager.merge(data);
    }

    @Override
    public UserCurrentHealth findUser(Users user){
        TypedQuery<UserCurrentHealth> query = entityManager.createQuery("from UserCurrentHealth where user = :user",UserCurrentHealth.class);

        query.setParameter("user",user);
        query.setMaxResults(1);

        List<UserCurrentHealth> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public void saveUserCurrentHealth(UserCurrentHealth theUser){
        entityManager.merge(theUser);
    }

    @Override
    public UserProfile findUserProfileByUser(Users user){
        TypedQuery<UserProfile> query = entityManager.createQuery("from UserProfile where user = :user",UserProfile.class);

        query.setParameter("user",user);
        query.setMaxResults(1);

        List<UserProfile> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

    @Override
    public UserGoal findGoalByUserId(int userId){
        TypedQuery<UserGoal> query = entityManager.createQuery("FROM UserGoal g WHERE g.user.id = :userId",UserGoal.class);

        query.setParameter("userId",userId);
        query.setMaxResults(1);

        List<UserGoal> theUser = query.getResultList();
        return theUser.isEmpty() ? null : theUser.get(0);
    }

}

package com.health.HealthSynqBackend.service;

import com.health.HealthSynqBackend.dao.AuthDao;
import com.health.HealthSynqBackend.dto.LoginDTO;
import com.health.HealthSynqBackend.dto.LoginResponse;
import com.health.HealthSynqBackend.dto.SignupResponse;
import com.health.HealthSynqBackend.dto.UserDTO;
import com.health.HealthSynqBackend.dto.UserCheckDTO;
import com.health.HealthSynqBackend.entities.UserGoal;
import com.health.HealthSynqBackend.entities.UserProfile;
import com.health.HealthSynqBackend.entities.Users;
import com.health.HealthSynqBackend.exception.InvalidCredentialException;
import com.health.HealthSynqBackend.exception.InvalidRequestException;
import com.health.HealthSynqBackend.exception.UserAlreadyExistsException;
import jakarta.transaction.Transactional;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class AuthServiceImpl implements AuthService{
    private AuthDao authDao;
    private BCryptPasswordEncoder bCryptPasswordEncoder;

    public AuthServiceImpl(AuthDao theAuthDao,BCryptPasswordEncoder theBcryptPasswordEncoder){
        authDao = theAuthDao;
        bCryptPasswordEncoder = theBcryptPasswordEncoder;
    }

    @Transactional
    public SignupResponse saveUser(UserDTO theUser){
        SignupResponse signupResponse = new SignupResponse();

        if(theUser==null){
            signupResponse.setSuccess(false);
            signupResponse.setMessage("Invalid Request: Empty Body");
            signupResponse.setStatusCode(400);
            signupResponse.setTimeStamp(System.currentTimeMillis());
            return signupResponse;
        }

        if (theUser.getEmail() == null || theUser.getEmail().isBlank() ||
                theUser.getPassword() == null || theUser.getPassword().isBlank() ||
                theUser.getGender() == null || theUser.getGender().isBlank() ||
                theUser.getWeightType() == null || theUser.getWeightType().isBlank() ||
                theUser.getHeightType() == null || theUser.getHeightType().isBlank() ||
                theUser.getTargetWeightType() == null || theUser.getTargetWeightType().isBlank() ||
                theUser.getUserName() == null || theUser.getUserName().isBlank() ||
                theUser.getAge() == null ||
                theUser.getWeight() == null ||
                theUser.getHeight() == null ||
                theUser.getTargetWeight() == null ||
                theUser.getTargetDurationDays() == null ||
                theUser.getIsDiabetic() == null) {

            signupResponse.setSuccess(false);
            signupResponse.setMessage("Missing required fields");
            signupResponse.setStatusCode(400);
            signupResponse.setTimeStamp(System.currentTimeMillis());
            return signupResponse;
        }

        // Email Validation

        String email = theUser.getEmail().trim().toLowerCase();

        if (!email.matches("^[A-Za-z0-9._%+-]+@(gmail|googlemail)\\.[A-Za-z.]+$")) {
            throw new InvalidRequestException("Invalid Gmail format");
        }
        theUser.setEmail(email);

        if(authDao.existByEmail(email)){
            throw new UserAlreadyExistsException("User Aleady Exists!");
        }

        // Password Validation and Conversion to Bcrypt
        String password = theUser.getPassword();
        if(password.length()<6){
            throw new InvalidRequestException("Password length is less");
        }
        try{
            String hashed = bCryptPasswordEncoder.encode(password);
            theUser.setPassword(hashed);
        }
        catch (Exception e){
            throw e;
        }

        // Age Validaton
        if(theUser.getAge()<=5 || theUser.getAge()>100){
            throw new InvalidRequestException("Invalid Age");
        }

        // Gender Validation
        theUser.setGender(theUser.getGender().toLowerCase());
        if(!theUser.getGender().equals("male") && !theUser.getGender().equals("female")){
            throw new InvalidRequestException("Invalid Gender");
        }

        // Weight Validation
        validateWeight(theUser.getWeight(), theUser.getWeightType());

        // Height Validation
        validateHeight(theUser.getHeight(), theUser.getHeightType());

        // TargetWeight Validation
        validateWeight(theUser.getTargetWeight(), theUser.getTargetWeightType());

        // TargetDuration Days evaluation
        if(theUser.getTargetDurationDays()<10 || theUser.getTargetDurationDays()>365){
            throw new InvalidRequestException("Invalid Target Days Duration");
        }

        System.out.println(theUser);

        Users user = new Users(theUser.getEmail(), theUser.getUserName(), theUser.getPassword(), LocalDateTime.now());
        authDao.saveUser(user);

        long weightGm = convertWeightToGrams(theUser.getWeight(), theUser.getWeightType());
        int heightCm = convertHeightToCm(theUser.getHeight(),theUser.getHeightType());
        long targetWeightGm = convertWeightToGrams(theUser.getTargetWeight(), theUser.getTargetWeightType());
        double bmi = calculateBMI(weightGm,heightCm);

        UserProfile userProfile = new UserProfile(theUser.getAge(), theUser.getGender(), heightCm,weightGm, theUser.getIsDiabetic(), bmi);
        userProfile.setUser(user);
        authDao.saveUserProfile(userProfile);

        UserGoal userGoal = new UserGoal(targetWeightGm,theUser.getTargetDurationDays(),LocalDateTime.now());
        userGoal.setUser(user);
        authDao.saveUserGoal(userGoal);

        signupResponse.setSuccess(true);
        signupResponse.setMessage("User registered successfully");
        signupResponse.setStatusCode(201);
        signupResponse.setTimeStamp(System.currentTimeMillis());

        return signupResponse;
    }

    public SignupResponse existUser(UserCheckDTO theUser){

        if((theUser.getEmail() == null || theUser.getEmail().isBlank()) &&
                (theUser.getUserName() == null || theUser.getUserName().isBlank())) {

            throw new InvalidRequestException("Email or Username is required");
        }

        if((theUser.getEmail() != null && !theUser.getEmail().isBlank()) &&
                (theUser.getUserName() != null && !theUser.getUserName().isBlank())) {

            throw new InvalidRequestException("Only one field allowed: email OR username");
        }

        boolean ans;



        if(theUser.getEmail() != null && !theUser.getEmail().isBlank()){
            String email = theUser.getEmail().trim().toLowerCase();

            if (!email.matches("^[A-Za-z0-9._%+-]+@(gmail|googlemail)\\.[A-Za-z.]+$")) {
                throw new InvalidRequestException("Invalid Gmail format");
            }
            theUser.setEmail(email);
            ans = authDao.existByEmail(theUser.getEmail());
        } else {
            ans = authDao.existByUserName(theUser.getUserName());
        }

        SignupResponse response = new SignupResponse();

        response.setTimeStamp(System.currentTimeMillis());
        response.setStatusCode(200);

        if(ans){
            response.setSuccess(false);
            response.setMessage("Email/Username already exists");
        } else {
            response.setSuccess(true);
            response.setMessage("Email/Username available");
        }

        return response;
    }

    public LoginResponse loginUser(LoginDTO theUser){
        String identifier = theUser.getIdentifier();
        identifier = identifier.trim();

        if(identifier == null || identifier.isBlank()){
            throw new InvalidCredentialException("Identifier cannot be empty");
        }

        if(theUser.getPassword()==null || theUser.getPassword().isEmpty()){
            throw new InvalidCredentialException("Password cannot be empty");
        }

        Users dbUser = authDao.findUser(identifier);
        LoginResponse response = new LoginResponse();

        if(dbUser==null){
            throw new InvalidCredentialException("Invalid Username/Email");
        }

        if(!bCryptPasswordEncoder.matches(theUser.getPassword(),dbUser.getPassword())){
            throw new InvalidCredentialException("Password mismatch");
        }
        return new LoginResponse(200, "Login Successful",true,System.currentTimeMillis());
    }

    private double calculateBMI(long weightGrams, int heightCm){

        double weightKg = weightGrams / 1000.0;
        double heightMeters = heightCm / 100.0;

        double bmi = weightKg / (heightMeters * heightMeters);

        return Math.round(bmi * 100.0) / 100.0;
    }

    private int convertHeightToCm(int height, String heightType){

        if(heightType.equalsIgnoreCase("cm")){
            return height;
        }

        if(heightType.equalsIgnoreCase("in")){
            return (int)Math.round(height * 2.54);
        }

        return 0; // should never happen since validation is already done
    }

    private long convertWeightToGrams(int weight, String weightType){

        if(weightType.equalsIgnoreCase("kg")){
            return weight * 1000L;
        }

        if(weightType.equalsIgnoreCase("lb")){
            return (long)(weight * 453.592);
        }

        return 0; // this should never happen since validation is already done
    }

    private void validateWeight(Integer weight, String weightType){
        weightType = weightType.toLowerCase();
        if(weightType.equalsIgnoreCase("kg")){
            if(weight < 20 || weight > 300){
                throw new InvalidRequestException("Weight out of valid range for kg");
            }
        }
        else if(weightType.equalsIgnoreCase("lb")){
            if(weight < 40 || weight > 660){
                throw new InvalidRequestException("Weight out of valid range for lb");
            }
        }
        else{
            throw new InvalidRequestException("Invalid Weight Type");
        }
    }
    private void validateHeight(Integer height, String heightType){
        if(heightType.equalsIgnoreCase("cm")){
            if(height < 80 || height > 250){
                throw new InvalidRequestException("Height out of valid range for cm");
            }
        }
        else if(heightType.equalsIgnoreCase("in")){
            if(height < 31 || height > 98){
                throw new InvalidRequestException("Height out of valid range for inches");
            }
        }
        else{
            throw new InvalidRequestException("Invalid height type");
        }
    }
}

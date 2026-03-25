package com.health.HealthSynqBackend.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.security.Key;
import java.util.Base64;
import java.util.Date;

@Service
public class JWTService {
    @Value("${jwt.secret}")
    private String SecretKey;

    private static final long EXPIRATION_TIME = 1000 * 60 * 60 * 24 * 15;

    private Key getSecretKey(){
        byte[] keyBytes = Base64.getDecoder().decode(SecretKey);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(int id, String email){
        return Jwts.builder()
                .setSubject(email)
                .claim("userId",id)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis()+EXPIRATION_TIME))
                .signWith(getSecretKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public int extractUserId(String token) {
        Claims claims = extractAllClaims(token);

        Object userIdObj = claims.get("userId");

        if (userIdObj instanceof Integer) {
            return (Integer) userIdObj;
        } else if (userIdObj instanceof Long) {
            return ((Long) userIdObj).intValue();
        }

        throw new RuntimeException("Invalid userId type in token");
    }

    public String extractEmail(String token) {
        return extractAllClaims(token).getSubject();
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSecretKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public boolean isTokenValid(String token) {
        try {
            extractAllClaims(token);
            return true;
        } catch (io.jsonwebtoken.ExpiredJwtException e) {
            return false;
        } catch (Exception e) {
            return false;
        }
    }
}

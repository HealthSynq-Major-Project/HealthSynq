package com.health.HealthSynqBackend;

import jakarta.annotation.PostConstruct;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.TimeZone;

@SpringBootApplication
public class HealthSynqBackendApplication {
	public static void main(String[] args) {
		SpringApplication.run(HealthSynqBackendApplication.class, args);
	}
}

package com.health.HealthSynqBackend.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DemoController {
    @GetMapping("/ping")
    public String ping(){
        return "OK";
    }
}

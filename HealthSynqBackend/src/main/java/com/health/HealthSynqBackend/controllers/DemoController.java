package com.health.HealthSynqBackend.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DemoController {
    @GetMapping("/")
    public String defaultResult(){
        return "Server Bdhiya chl raha hai..... MAA CHUDAO";
    }

    @GetMapping("/ping")
    public String ping(){
        return "OK";
    }
}

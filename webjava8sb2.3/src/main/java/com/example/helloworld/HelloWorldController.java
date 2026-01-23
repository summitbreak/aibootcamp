package com.example.helloworld;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloWorldController {

    @GetMapping("/")
    public String home() {
        return "Hello World! Welcome to Spring Boot 2.3 with Java 8";
    }

    @GetMapping("/hello")
    public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
        return String.format("Hello, %s!", name);
    }

    @GetMapping("/info")
    public AppInfo info() {
        return new AppInfo(
            "Hello World Application",
            "1.0.0",
            "Spring Boot 2.3.12.RELEASE",
            "Java 8"
        );
    }

    static class AppInfo {
        private String name;
        private String version;
        private String springBootVersion;
        private String javaVersion;

        public AppInfo(String name, String version, String springBootVersion, String javaVersion) {
            this.name = name;
            this.version = version;
            this.springBootVersion = springBootVersion;
            this.javaVersion = javaVersion;
        }

        public String getName() {
            return name;
        }

        public String getVersion() {
            return version;
        }

        public String getSpringBootVersion() {
            return springBootVersion;
        }

        public String getJavaVersion() {
            return javaVersion;
        }
    }
}

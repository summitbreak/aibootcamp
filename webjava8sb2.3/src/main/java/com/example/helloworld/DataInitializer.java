package com.example.helloworld;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final PersonRepository personRepository;

    @Autowired
    public DataInitializer(PersonRepository personRepository) {
        this.personRepository = personRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        personRepository.save(new Person("John Doe", "john.doe@example.com"));
        personRepository.save(new Person("Jane Smith", "jane.smith@example.com"));
        personRepository.save(new Person("Bob Johnson", "bob.johnson@example.com"));
        personRepository.save(new Person("Alice Williams", "alice.williams@example.com"));
        personRepository.save(new Person("John Smith", "john.smith@example.com"));

        System.out.println("Sample data initialized successfully!");
    }
}

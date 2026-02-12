package com.example.helloworld;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PersonService {

    private final PersonRepository personRepository;

    @Autowired
    public PersonService(PersonRepository personRepository) {
        this.personRepository = personRepository;
    }

    public List<Person> findByName(String name) {
        return personRepository.findByName(name);
    }

    public List<Person> findByNameIgnoreCase(String name) {
        return personRepository.findByNameIgnoreCase(name);
    }

    public List<Person> searchByName(String name) {
        return personRepository.findByNameContainingIgnoreCase(name);
    }

    public List<Person> getAllPersons() {
        return personRepository.findAll();
    }

    public Person savePerson(Person person) {
        return personRepository.save(person);
    }
}

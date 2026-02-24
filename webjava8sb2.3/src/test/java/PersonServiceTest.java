package com.example.helloworld;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PersonServiceTest {

    @Mock
    private PersonRepository personRepository;

    @InjectMocks
    private PersonService personService;

    private Person john;
    private Person jane;

    @BeforeEach
    void setUp() {
        john = new Person("John Doe", "john.doe@example.com");
        john.setId(1L);
        jane = new Person("Jane Smith", "jane.smith@example.com");
        jane.setId(2L);
    }

    // --- getAllPersons ---

    @Test
    void getAllPersons_returnsAllPersons() {
        when(personRepository.findAll()).thenReturn(Arrays.asList(john, jane));

        List<Person> result = personService.getAllPersons();

        assertThat(result).hasSize(2).containsExactly(john, jane);
        verify(personRepository).findAll();
    }

    @Test
    void getAllPersons_returnsEmptyList_whenNoneExist() {
        when(personRepository.findAll()).thenReturn(Collections.emptyList());

        List<Person> result = personService.getAllPersons();

        assertThat(result).isEmpty();
    }

    // --- findByName ---

    @Test
    void findByName_returnsMatchingPersons() {
        when(personRepository.findByName("John Doe")).thenReturn(List.of(john));

        List<Person> result = personService.findByName("John Doe");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("John Doe");
    }

    @Test
    void findByName_returnsEmpty_whenNoMatch() {
        when(personRepository.findByName("Unknown")).thenReturn(Collections.emptyList());

        List<Person> result = personService.findByName("Unknown");

        assertThat(result).isEmpty();
    }

    // --- findByNameIgnoreCase ---

    @Test
    void findByNameIgnoreCase_returnsMatchRegardlessOfCase() {
        when(personRepository.findByNameIgnoreCase("john doe")).thenReturn(List.of(john));

        List<Person> result = personService.findByNameIgnoreCase("john doe");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("John Doe");
    }

    @Test
    void findByNameIgnoreCase_returnsEmpty_whenNoMatch() {
        when(personRepository.findByNameIgnoreCase("nobody")).thenReturn(Collections.emptyList());

        List<Person> result = personService.findByNameIgnoreCase("nobody");

        assertThat(result).isEmpty();
    }

    // --- searchByName (partial match) ---

    @Test
    void searchByName_returnsPartialMatches() {
        when(personRepository.findByNameContainingIgnoreCase("john")).thenReturn(Arrays.asList(john, jane));

        List<Person> result = personService.searchByName("john");

        assertThat(result).hasSize(2);
    }

    @Test
    void searchByName_isCaseInsensitive() {
        when(personRepository.findByNameContainingIgnoreCase("JANE")).thenReturn(List.of(jane));

        List<Person> result = personService.searchByName("JANE");

        assertThat(result).containsExactly(jane);
    }

    @Test
    void searchByName_returnsEmpty_whenNoMatch() {
        when(personRepository.findByNameContainingIgnoreCase("xyz")).thenReturn(Collections.emptyList());

        List<Person> result = personService.searchByName("xyz");

        assertThat(result).isEmpty();
    }

    // --- savePerson ---

    @Test
    void savePerson_returnsSavedPerson() {
        Person newPerson = new Person("Alice", "alice@example.com");
        Person saved = new Person("Alice", "alice@example.com");
        saved.setId(3L);

        when(personRepository.save(newPerson)).thenReturn(saved);

        Person result = personService.savePerson(newPerson);

        assertThat(result.getId()).isEqualTo(3L);
        assertThat(result.getName()).isEqualTo("Alice");
        verify(personRepository).save(newPerson);
    }

    @Test
    void savePerson_callsRepositorySaveOnce() {
        Person person = new Person("Bob", "bob@example.com");
        when(personRepository.save(person)).thenReturn(person);

        personService.savePerson(person);

        verify(personRepository, times(1)).save(person);
    }
}

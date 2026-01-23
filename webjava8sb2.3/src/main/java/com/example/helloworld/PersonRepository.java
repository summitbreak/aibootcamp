package com.example.helloworld;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PersonRepository extends JpaRepository<Person, Long> {

    List<Person> findByName(String name);

    List<Person> findByNameContainingIgnoreCase(String name);

    @Query("SELECT p FROM Person p WHERE LOWER(p.name) = LOWER(:name)")
    List<Person> findByNameIgnoreCase(@Param("name") String name);
}

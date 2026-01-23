# Hello World Spring Boot Application

A simple Hello World web application built with Java 8 and Spring Boot 2.3.12.

## Prerequisites

- Java 8 (JDK 1.8)
- Maven 3.x

## Build and Run

### Using Maven

```bash
# Build the application
mvn clean package

# Run the application
mvn spring-boot:run
```

### Using Java

```bash
# Build first
mvn clean package

# Run the JAR
java -jar target/hello-world-app-1.0.0.jar
```

## Available Endpoints

Once the application is running, access these endpoints:

### Basic Endpoints
- `http://localhost:8080/` - Home page with welcome message
- `http://localhost:8080/hello` - Hello endpoint (default: "Hello, World!")
- `http://localhost:8080/hello?name=YourName` - Personalized greeting
- `http://localhost:8080/info` - Application information (JSON)

### Database Endpoints
- `GET http://localhost:8080/api/persons` - Get all persons from database
- `GET http://localhost:8080/api/persons/search?name=John` - Search persons by exact name (case-insensitive)
- `GET http://localhost:8080/api/persons/search-partial?name=john` - Search persons by partial name match
- `POST http://localhost:8080/api/persons` - Create a new person

### H2 Database Console
- `http://localhost:8080/h2-console` - H2 database web console
  - JDBC URL: `jdbc:h2:mem:testdb`
  - Username: `sa`
  - Password: (leave empty)

## Testing

```bash
# Basic endpoints
curl http://localhost:8080/
curl http://localhost:8080/hello
curl http://localhost:8080/hello?name=John
curl http://localhost:8080/info

# Database endpoints
curl http://localhost:8080/api/persons
curl "http://localhost:8080/api/persons/search?name=John"
curl "http://localhost:8080/api/persons/search-partial?name=john"

# Create a new person
curl -X POST http://localhost:8080/api/persons \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'
```

## Sample Data

The application initializes with the following sample data:
- John Doe (john.doe@example.com)
- Jane Smith (jane.smith@example.com)
- Bob Johnson (bob.johnson@example.com)
- Alice Williams (alice.williams@example.com)
- John Smith (john.smith@example.com)

## Project Structure

```
.
├── pom.xml
├── src
│   ├── main
│   │   ├── java
│   │   │   └── com
│   │   │       └── example
│   │   │           └── helloworld
│   │   │               ├── HelloWorldApplication.java
│   │   │               └── HelloWorldController.java
│   │   └── resources
│   │       └── application.properties
│   └── test
│       └── java
│           └── com
│               └── example
│                   └── helloworld
└── README.md
```

## Technologies Used

- Java 8
- Spring Boot 2.3.12.RELEASE
- Spring Web
- Spring Data JPA
- H2 Database (embedded)
- Maven

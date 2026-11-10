FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /src
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /src/target/acl-01-anticorrupcion.jar app.jar
ENV PUERTO=8010
EXPOSE 8010
CMD ["java", "-jar", "app.jar"]

FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /src
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /src/target/vencimientos.jar app.jar
ENV PUERTO=8002
EXPOSE 8002
CMD ["java", "-jar", "app.jar"]

# Created by santunioni at 2/15/22
Feature: FastAPI rate limiting

  Background:
    Given A Rest API built with FastAPI


  Scenario: There is a global limiter in the API
    Given The API is limited globally to 10 requests per 1 seconds
    When I hit the API 10 times in a row
    Then All responses are successful
    But The next hit is blocked by the limiter
    And I should only retry after 1 seconds


  Scenario: The limiter is ignoring a given path
    Given The API is limited globally to 5 requests per 1 seconds
    But The limiter ignores the path being tested
    When I hit the API 30 times in a row
    Then All responses are successful

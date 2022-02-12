## 0.1.16a32 (2022-02-12)

## 0.1.16a31 (2022-02-12)

## 0.1.16a30 (2022-02-12)

## 0.1.16a29 (2022-02-12)

### Refactor

- make strategies a Enum

### Feat

- implement strategies with redis storage
- implement redis storage
- add decr method to MemoryWindow

## 0.1.16a28 (2022-02-08)

## 0.1.16a27 (2022-02-08)

## 0.1.16a26 (2022-02-07)

## 0.1.16a25 (2022-02-07)

### Fix

- cast retry-after http header
- window duration in fixed window strategy for memory storage

## 0.1.16a24 (2022-02-07)

### Fix

- add cast to str in exc.retry_after

## 0.1.16a23 (2022-02-07)

### Fix

- check if FastAPILimiter instead of Limiter

## 0.1.16a21 (2022-02-07)

## 0.1.16a20 (2022-02-03)

## 0.1.16a19 (2022-02-03)

### Refactor

- fastapi limiters

## 0.1.16a18 (2022-01-30)

### Feat

- implement moving window for memory storage

### Perf

- optimize fixed window strategy

## 0.1.16a17 (2022-01-25)

## 0.1.16a16 (2022-01-25)

## 0.1.16a15 (2022-01-24)

### Refactor

- fastapi module

## 0.1.16a14 (2022-01-23)

### Fix

- remove exception being raised improperty in fastapi.builter

## 0.1.16a13 (2022-01-23)

### Fix

- implement abstract method

## 0.1.16a12 (2022-01-23)

### Refactor

- extract Limiter

## 0.1.16a11 (2022-01-23)

### Fix

- wrong import

## 0.1.16a10 (2022-01-23)

## 0.1.16a9 (2022-01-23)

### Fix

- window strategy

## 0.1.16a8 (2022-01-23)

### Fix

- middleware

## 0.1.16a7 (2022-01-23)

## 0.1.16a6 (2022-01-22)

## 0.1.16a5 (2022-01-22)

### Fix

- remove updating dependencies after creating app

## 0.1.16a4 (2022-01-22)

### Feat

- add ignored paths to middleware

## 0.1.16a3 (2022-01-22)

## 0.1.16a2 (2022-01-22)

### Perf

- add middlewares for better performance

## 0.1.16a1 (2022-01-22)

### Fix

- import time in models
- import time in models

## 0.1.16a0 (2022-01-22)

## 0.1.15 (2022-01-22)

### Fix

- change precision to microseconds

## 0.1.14 (2022-01-22)

## 0.1.13 (2022-01-22)

## 0.1.12 (2022-01-22)

## 0.1.11 (2022-01-22)

### Fix

- wrong import

## 0.1.10 (2022-01-22)

### Feat

- host based limiter

## 0.1.9 (2022-01-22)

### Feat

- fixed window block based on key

## 0.1.8 (2022-01-22)

### Fix

- wrong import

## 0.1.7 (2022-01-22)

## 0.1.6 (2022-01-22)

### Feat

- add retry-after to handler

## 0.1.5 (2022-01-22)

### Feat

- add retry-after

## 0.1.4 (2022-01-22)

### Feat

- add handler for fastapi

## 0.1.3 (2022-01-22)

### Fix

- wrong import

## 0.1.2 (2022-01-22)

### Feat

- add simple limiter for fastapi

## 0.1.1 (2022-01-18)

### Perf

- optimize Rate.create_from_hits for memory

### Feat

- implement models

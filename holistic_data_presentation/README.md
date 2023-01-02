# API Documentation

## Data Presentation
Any request to the API, needs to provide the following HTTP Header.

```
Authorization: Token <AUTH TOKEN>
```

## All-Time Number of Therapist API
- `GET /total-therapists/all-time/`
  <br/><br/>The `TotalTherapist` data object has the following format:
  ```json
  {
    "start_date": "2022-10-30",
    "end_date": "2022-11-05",
    "is_active": true,
    "value": 10
  }
  ```
- `POST /total-therapists/all-time/`
  <br/><br/>Request Body:

  ```json
  {
    "start_date":"2022-10-30",
    "end_date": "2022-11-05",
    "is_active": true,
    "value": 10
  }
  ```

  Response data has the following format:
  ```json
  {
    "start_date":"2022-10-30",
    "end_date": "2022-11-05",
    "is_active": true,
    "value": 10
  }
  ```

## Number of Therapist API
- `GET /total-therapists/`
  <br/><br/>The `TotalTherapist` data object has the following format:
  ```json
  {
    "period_type": "weekly",
    "organization": 1,
    "start_date": "2022-10-30",
    "end_date": "2022-11-05",
    "is_active": true,
    "value": 10
  }
  ```
- `POST /organizations/<id>/total-therapists/`
  <br/><br/>Request Body:

  ```json
  [
    {"period_type": "weekly", "start_date":"2022-10-30", "end_date": "2022-11-05", "is_active": true, "value": 10},
    {"period_type": "weekly", "start_date":"2022-11-06", "end_date": "2022-11-12", "is_active": false, "value": 11},
    {"period_type": "weekly", "start_date":"2022-11-13", "end_date": "2018-11-19", "is_active": true, "value": 29}
  ]
  ```

  Response data has the following format:
  ```json
  {
    "rows_created": 2,
    "rows_updated": 0
  }
  ```


## Organization Rate API
- `GET /rates/`
  <br/><br/>The `TherapistRate` data object has the following format:
  ```json
  {
    "organization": 1,
    "period_type": "weekly",
    "start_date": "2022-10-30",
    "end_date": "2022-11-05",
    "type": "churn_rate",
    "rate_value": 2.5
  }
  ```
- `POST /organizations/<id>/rates/`
  <br/><br/>The `TherapistRate` data object has the following format:
  ```json
  [
    {"type": "churn_rate", "period_type": "weekly", "start_date":"2022-10-30", "end_date": "2022-11-05", "rate_value": 1.5},
    {"type": "churn_rate", "period_type": "weekly", "start_date":"2022-11-06", "end_date": "2022-11-12", "rate_value": 2.5},
    {"type": "retention_rate", "period_type": "weekly", "start_date":"2022-10-30", "end_date": "2022-11-05", "rate_value": 3.5},
    {"type": "retention_rate", "period_type": "weekly", "start_date":"2022-11-06", "end_date": "2022-11-12", "rate_value": 1.7}
  ]
  ```

  Response data has the following format:
  ```json
  {
    "rows_created": 4,
    "rows_updated": 0
  }
  ```

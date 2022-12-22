# API Documentation

## Data Presentation
Any request to the API, needs to provide the following HTTP Header.

```
Authorization: Token <AUTH TOKEN>
```

## Number of Therapist API
- `GET /data-presentation/organizations/number-of-therapists/`
  <br/><br/>The `NumberOfTherapist` data object has the following format:
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
- `GET /data-presentation/organizations/<id>/number-of-therapists/`
  <br/><br/>The `NumberOfTherapist` data object has the following format:
  ```json
  {
    "organization": 1,
    "start_date": "2022-10-30",
    "end_date": "2022-11-05",
    "is_active": true,
    "value": 10
  }
  ```
- `POST /data-presentation/organizations/<id>/number-of-therapists/`
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

## Churn/Retention Rate API
- `GET /data-presentation/organizations/rates/`
  <br/><br/>The `OrganizationRate` data object has the following format:
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
- `GET /data-presentation/organizations/<id>/rates/`
  <br/><br/>The `OrganizationRate` data object has the following format:
  ```json
  {
    "period_type": "weekly",
    "start_date": "2022-10-30",
    "end_date": "2022-11-05",
    "type": "churn_rate",
    "rate_value": 1.5
  }
  ```
- `POST /data-presentation/organizations/<id>/rates/`
  <br/><br/>The `OrganizationRate` data object has the following format:
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

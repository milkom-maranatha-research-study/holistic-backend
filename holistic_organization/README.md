# API Documentation

## Authentication
Any request to the API, needs to provide the following HTTP Header.

```
Authorization: Token <AUTH TOKEN>
```

## Organization API
- `GET /organizations/`
  <br/><br/>The `Organization` data object has the following format:
  ```json
  {
    "id": 1,
    "name": "Organization 1"
  }
  ```

## Export Data API
- `POST /therapists/export/`
  <br/><br/>Request Body:

  ```json
  {"format": "csv|json"},
  ```

  Response data of the JSON format:
  ```json
  [
    {
      "therapist_id": "ther-id",
      "organization_id":1,
      "date_joined":"2018-06-08"
    }
  ]
  ```

  Response data of the CSV format:
  ```
  therapist_id,organization_id,date_joined
  "ther-id",1,"2018-06-08"
  ```
- `POST /interactions/export/`
  <br/><br/>Request Body:

  ```json
  {"format": "csv|json"},
  ```

  Response data of the JSON format:
  ```json
  [
    {
      "therapist_id": "ther-id",
      "interaction_date":"2018-06-08",
      "counter":1,
      "chat_count":2,
      "call_count":0,
      "organization_id":1,
      "organization_date_joined":"2018-06-08"
    }
  ]
  ```

  Response data of the CSV format:
  ```
  therapist_id,interaction_date,counter,chat_count,call_count,organization_id,organization_date_joined
  "ther-id","2018-06-08",1,2,0,1,"2018-06-08"
  ```

## Organization Synchronization API
- `POST /sync/organizations/`
  <br/><br/>Request Body:

  ```json
  [
    {"organization_id":1},
    {"organization_id":2}
  ]
  ```

  Response data has the following format:
  ```json
  {
    "rows_created": 2
  }
  ```

## Therapists Synchronization API
- `POST /sync/organizations/<id>/therapists/`
  <br/><br/>Request Body:

  ```json
  [  
    {"date_joined":"2018-04-06","therapist_id":"c55a11c49fb2c631455f4549b94a7383"},
    {"date_joined":"2018-04-06","therapist_id":"db57d9327d2af238b1661484bd2ba86d"},
    {"date_joined":"2018-06-17","therapist_id":"2d8023ddb77664de44bf3ac8d46890da"}
  ]
  ```

  Response data has the following format:
  ```json
  {
    "rows_created": 3,
    "rows_updated": 0
  }
  ```

## Interactions Synchronization API
- `POST /sync/therapists/<id>/interactions/`
  <br/><br/>Request Body:

  ```json
  [
    {"interaction_date":"2018-06-08","counter":1,"chat_count":2,"call_count":0},
    {"interaction_date":"2018-06-13","counter":1,"chat_count":1,"call_count":0},
    {"interaction_date":"2018-06-13","counter":2,"chat_count":2,"call_count":0},
    {"interaction_date":"2018-06-14","counter":1,"chat_count":2,"call_count":13},
    {"interaction_date":"2018-06-14","counter":2,"chat_count":1,"call_count":0},
    {"interaction_date":"2018-06-14","counter":3,"chat_count":1,"call_count":0},
    {"interaction_date":"2018-06-15","counter":1,"chat_count":14,"call_count":0},
    {"interaction_date":"2018-06-16","counter":1,"chat_count":0,"call_count":0}
  ]
  ```

  Response data has the following format:
  ```json
  {
    "rows_created": 8,
    "rows_updated": 0
  }
  ```

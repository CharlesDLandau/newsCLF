# Text Pipeliner API

Currently the Text Pipeliner API supports just two endpoints.

## 1: GET registers
```Endpoint: /api/pickleregister?id=None```


```Method: GET```


```Response: JSON - the entire registry, or a single entry (by id)```
 
## 2: POST for predictions
```Endpoint: /api/predict```


```Method: POST```


```Response: JSON - the prediction, and the registry entry for the pipeline ```

## Query the register:

Querying the register will return a JSON object in the form:

```
{
    "register": JSON array: register
}
```

Querying the register with a valid ID will return a JSON object in the form:

```
{
    "register": JSON object: register entry
}
```

## Predict with Text Pipeliner

/api/predict POST expects some JSON in the form:

```
{
    "id": "pickle0001",
    "text": string
}
```


With a valid ID, it returns the prediction and the register entry

```
{
    "register": register entry
    "prediction": string 
}
```

# WARNING:
The API is not frozen.
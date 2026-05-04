from prometheus_client import Counter, Histogram 

PREDICTION_COUNT = Counter( # Count how many times event happens
    "prediction_requests_total", # name 
    "Total number of prediction requests", # desc 
    ["label"] # labelnames, 0/1
)

PREDICTION_ROWS = Histogram( # measure: latency, rows, file size => 
    "prediction_rows_per_request",
    "Number of rows per prediction request",
    buckets=[1, 5, 10, 50, 100, 500] # each bucket count all values <= threshold (cumulative):
)

import logging 
import json 

class JsonFormatter(logging.Formatter):
    def format(self, record): 
        return json.dumps({
            "timestamp": self.formatTime(record), 
            "level": record.levelname, 
            "message": record.getMessage(), 
            **getattr(record, "extra", {})
        })
    
def get_logger(name: str) -> logging.Logger: 
    handler = logging.StreamHandler() 
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger 
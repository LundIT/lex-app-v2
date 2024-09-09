import contextvars
from uuid import uuid4

# Define a context variable
context_id = contextvars.ContextVar('context_id', default=None)

# Context manager to set operation id
class OperationContext:
    
    def __init__(self, request):
        self.request = request
    
    def __enter__(self):
        # Set a new operation id if one doesn't already exist
        if context_id.get() is None:
            context_id.set({'context_id': str(uuid4()),
                            'request_obj': self.request})
        return context_id.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Optionally, reset or clear the operation id here if necessary
        pass
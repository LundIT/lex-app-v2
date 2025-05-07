import contextvars
from contextlib import contextmanager

# holds a list of model instances, from “root” → “current”
_model_stack: contextvars.ContextVar[list] = contextvars.ContextVar('model_stack', default=[])

@contextmanager
def model_logging_context(instance):
    """
    Push `instance` onto the model‐stack for any nested calls,
    then pop it back off when the block exits.
    """
    stack = _model_stack.get()
    # set returns a Token we can use to reset later
    token = _model_stack.set(stack + [instance])
    try:
        yield
    except Exception as e:
        # Log the exception with the current instance
        print(f"Error in model context with instance {instance}: {e}")
        raise
    finally:
        _model_stack.reset(token)
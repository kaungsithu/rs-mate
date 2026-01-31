"""Error handling and user feedback components."""
from fasthtml.common import *
from monsterui.all import *

__all__ = [
    'mk_error_alert', 'mk_warning_alert', 'mk_info_alert', 'mk_success_alert',
    'mk_connection_error', 'mk_not_found_error', 'mk_permission_error',
    'mk_validation_error', 'ErrorType'
]


class ErrorType:
    """Error type constants."""
    CONNECTION = 'connection'
    NOT_FOUND = 'not_found'
    PERMISSION = 'permission'
    VALIDATION = 'validation'
    SERVER = 'server'
    UNKNOWN = 'unknown'


def mk_error_alert(title: str, message: str, dismissible: bool = True) -> Div:
    """Create error alert component."""
    alert = Alert(
        Div(
            H5(title, cls='font-bold'),
            P(message)
        ),
        cls=AlertT.danger
    )
    if dismissible:
        return Div(
            alert,
            Button('Dismiss', cls=ButtonT.ghost + ' float-right', hx_swap='outerHTML swap:1s'),
            cls='relative'
        )
    return alert


def mk_warning_alert(title: str, message: str, dismissible: bool = True) -> Div:
    """Create warning alert component."""
    alert = Alert(
        Div(
            H5(title, cls='font-bold'),
            P(message)
        ),
        cls=AlertT.warning
    )
    if dismissible:
        return Div(
            alert,
            Button('Dismiss', cls=ButtonT.ghost + ' float-right', hx_swap='outerHTML swap:1s'),
            cls='relative'
        )
    return alert


def mk_info_alert(title: str, message: str, dismissible: bool = True) -> Div:
    """Create info alert component."""
    alert = Alert(
        Div(
            H5(title, cls='font-bold'),
            P(message)
        ),
        cls=AlertT.info
    )
    if dismissible:
        return Div(
            alert,
            Button('Dismiss', cls=ButtonT.ghost + ' float-right', hx_swap='outerHTML swap:1s'),
            cls='relative'
        )
    return alert


def mk_success_alert(title: str, message: str, dismissible: bool = True) -> Div:
    """Create success alert component."""
    alert = Alert(
        Div(
            H5(title, cls='font-bold'),
            P(message)
        ),
        cls=AlertT.success
    )
    if dismissible:
        return Div(
            alert,
            Button('Dismiss', cls=ButtonT.ghost + ' float-right', hx_swap='outerHTML swap:1s'),
            cls='relative'
        )
    return alert


def mk_connection_error(detail: str = None) -> Div:
    """Create connection error component."""
    message = 'Unable to connect to Redshift cluster.'
    if detail:
        message += f' {detail}'
    return mk_error_alert(
        'Connection Error',
        message + ' Please check your connection settings and try again.'
    )


def mk_not_found_error(entity_type: str, entity_name: str) -> Div:
    """Create not found error component."""
    return mk_error_alert(
        'Not Found',
        f'{entity_type} "{entity_name}" could not be found. It may have been deleted.'
    )


def mk_permission_error(action: str, entity_type: str) -> Div:
    """Create permission error component."""
    return mk_error_alert(
        'Permission Denied',
        f'You do not have permission to {action} {entity_type.lower()}. '
        'Please contact your Redshift administrator.'
    )


def mk_validation_error(field: str, message: str) -> Div:
    """Create validation error component."""
    return mk_error_alert(
        'Validation Error',
        f'{field}: {message}'
    )


def safe_execute(fn, error_title: str = 'Error', error_context: str = None):
    """Execute function with error handling.

    Args:
        fn: Function to execute
        error_title: Title for error alert if exception occurs
        error_context: Additional context for error message

    Returns:
        Tuple of (success: bool, result or error_component)
    """
    try:
        return True, fn()
    except ValueError as e:
        msg = f'Invalid value: {str(e)}'
        if error_context:
            msg += f' ({error_context})'
        return False, mk_error_alert(error_title, msg)
    except KeyError as e:
        msg = f'Missing required field: {str(e)}'
        if error_context:
            msg += f' ({error_context})'
        return False, mk_error_alert(error_title, msg)
    except PermissionError as e:
        msg = f'Permission denied: {str(e)}'
        if error_context:
            msg += f' ({error_context})'
        return False, mk_permission_error('perform this action', 'this resource')
    except RuntimeError as e:
        msg = str(e)
        if error_context:
            msg += f' ({error_context})'
        return False, mk_error_alert(error_title, msg)
    except Exception as e:
        msg = f'An unexpected error occurred: {str(e)}'
        if error_context:
            msg += f' ({error_context})'
        return False, mk_error_alert(error_title, msg)

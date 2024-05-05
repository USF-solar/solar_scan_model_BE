"""
Create custom exception handler
"""

import sys

def error_message_detail(error, error_detail: sys):
    """
    Creates a human readable error message
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_num = exc_tb.tb_lineno
    error_str = str(error)
    
    error_message = f'Error occurred in Python script [{file_name}] \
        line [{line_num}] error message [{error_str}]'
    
    return error_message

class CustomException(Exception):
    """
    Class to call and generate the human readable error
    """

    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

        def __str__(self):
            return self.error_message
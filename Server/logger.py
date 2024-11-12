import logging
import os

class Logger:
    '''
    Clase para manejar los logs del servidor
    
    '''
    def __init__(self, debug=False):
        self.logger = logging.getLogger('Server')
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s- [%(levelname)s] - (%(threadName)s): %(message)s')

        current_dir = os.path.dirname(os.path.abspath(__file__))

        log_file_path = os.path.join(current_dir, 'log.txt')

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

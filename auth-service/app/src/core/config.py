import logging

# Create a custom logger
logger = logging.getLogger('movie_application')
logger.setLevel(logging.INFO)


# Create handlers
f_handler = logging.FileHandler("file.log", mode="w")

# Create formatters and add it to handlers

f_format = logging.Formatter(
    fmt='%(asctime)s %(levelname)-8s [%(filename)-16s:%(lineno)-5d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(f_handler)

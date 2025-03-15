#!/bin/bash
# gunicorn --bind 0.0.0.0:$PORT app:app

#!/bin/bash
export PORT=${PORT:-8000}
python app.py
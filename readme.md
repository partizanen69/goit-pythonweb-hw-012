```
poetry config virtualenvs.in-project true
poetry init -n --python '^3.12'
poetry env use $(which python3)
eval $(poetry env activate)
poetry add $(cat requirements.txt | awk '{print $1}')
poetry install --no-root
poetry env info


poetry add alembic
alembic init migrations

alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head

# run app
docker compose up
python main.py

# run tests
PYTHONPATH=$PYTHONPATH:. pytest tests/
PYTHONPATH=$PYTHONPATH:. pytest tests/ --cov=src --cov-report=term
pytest --cov=src
```

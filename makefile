server:
	uvicorn app.main:app --reload

lint:
	black . && isort .
## **Project Setup**

Run Project
1.Create .env file in backend folder and copy the contents of env.sample to .env file
2. docker compose build
3. docker compose up
4. docker exec -it app bash -> python manage.py migrate
5. docker exec -it app bash -> python manage.py createsuperuser #optional

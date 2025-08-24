import os
from dotenv import load_dotenv
import praw

# Загружаем переменные из .env
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    redirect_uri="http://localhost:8080",   # URL-редирект, который указан в настройках вашего Reddit-приложения
    user_agent=f"MyBot/1.0 by {os.getenv('REDDIT_USERNAME')}"
)

# Генерируем URL для авторизации
auth_url = reddit.auth.url(
    scopes=["read"],          # права, которые нужны вашему скраперу
    state="bitensor_state",   # любое случайное значение
    duration="permanent"      # permanent = refresh_token
)
print("1) Перейдите по этой ссылке, залогиньтесь и разрешите доступ:")
print(auth_url)
print("\n2) После авторизации вас редиректнет на URL вроде:")
print("   http://localhost:8080/?state=bitensor_state&code=ВАШ_КОД")
code = input("\n3) Вставьте сюда параметр code из URL: ").strip()

# Получаем refresh_token
refresh_token = reddit.auth.authorize(code)
print("\n=== Ваш новый REDDIT_REFRESH_TOKEN ===")
print(refresh_token)

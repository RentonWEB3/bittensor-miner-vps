Bittensor News Agent — Twitter-only (MVP)

Коротко: собираем твиты про Bittensor и его сабсети (SN#), автоматически отмечаем сабсети по алиасам, генерируем кандидаты твитов (≤280 символов, с #Bittensor) и публикуем вручную.

1) Цель и результат

Цель: сократить путь от сырого твита до готового короткого новостного поста для X/Twitter.

Результат (MVP):

Автопоток: Скрапинг (X) → RAW JSONL → Теггинг сабсетей → OpenAI → CANDIDATES JSONL → Ручная публикация.

Ежедневно появляются новые кандидаты твитов в out/candidates_tweets.jsonl.

Что вне MVP:

Reddit, Telegram, автопостинг, длинные статьи, сложные метрики — позже.

2) Аудитория

Энтузиасты и участники экосистемы Bittensor (TAO).

Валидаторы/майнеры сабсетей, ресёрчеры, крипто-SMM.

3) Источники и термины

Источник данных: только X/Twitter (по ключевым словам/алиасам).

Сабсеть (Subnet): обозначается как SN# (например, SN13).

Алиасы: словарь соответствий SN# ↔ названия/синонимы/хэштеги, хранится в data/aliases.json.

4) Поток данных (MVP Flow)

Скрапинг (twitter_scraper.py)
Собираем твиты по ключам/алиасам, записываем в БД как раньше и дополнительно в RAW JSONL.

RAW JSONL (data/raw/x.jsonl)
Каждая строка — один твит с полями (см. схему ниже).

Теггинг сабсетей
По data/aliases.json (регэкспы без ложных срабатываний) заполняем subnets[].

OpenAI (ai/summarize.py)
Из текста твита делаем кандидат твита (≤280, #Bittensor, в конце при наличии — (SN13, …)).

CANDIDATES JSONL (out/candidates_tweets.jsonl)
Складываем сгенерированные тексты с ссылкой на исходник.

Ручная публикация
Берём понравившиеся строки и постим в X.

5) Структура папок и файлов

PROJECT_ROOT/
  PROJECT_CONTEXT.md                ← этот файл
  scrapers/twikit_scraper.py       ← твой скрапер
  config/twitter_config.json        ← твой конфиг
  data/
    raw/x.jsonl                     ← сырые твиты (JSONL)
    aliases.json                    ← алиасы сабсетей (можно пустой {})
  out/
    candidates_tweets.jsonl         ← кандидаты твитов (JSONL)
  utils/
    jsonl.py                        ← append_jsonl(...)
    tagger.py                       ← detect_subnets(...)
  ai/
    summarize.py                    ← make_tweet(...)
  pipeline/
    read_incremental.py             ← iter_new_jsonl(...)
    run_once.py                     ← читает RAW → пишет CANDIDATES
  logs/
    pipeline.log
  .env                              ← OPENAI_API_KEY=...

6) Схема данных (кратко)
6.1 RAW (data/raw/x.jsonl) — одна JSON-строка = один твит

Обязательные поля:

{
  "id": "string",                           // ID твита на платформе
  "platform": "x",                          // всегда "x"
  "text": "string",                         // UTF-8, очищенный
  "url": "https://twitter.com/.../status/...", 
  "author": "string",                       // handle/username
  "created_at_source": "ISO8601",           // время из источника
  "scraped_at": "ISO8601",                  // локальное время скрапа
  "lang": "en|ru|und",
  "subnets": ["SN13"],                      // может быть []
  "topics": [],                             // не используется в MVP
  "is_reply": false,
  "is_repost": false,                       // retweet/repost
  "hash": "md5-of-normalized-text"          // для дедупликации
}

6.2 CANDIDATES (out/candidates_tweets.jsonl)

{
  "src_id": "string",                       // id из RAW
  "src_platform": "x",
  "src_url": "https://twitter.com/.../status/...",
  "created_at_source": "ISO8601",
  "generated_at": "ISO8601",
  "channel": "x",                           // всегда "x"
  "text": "string",                         // готовая строка для X (≤280)
  "model": "gpt-4o-mini",
  "tokens_prompt": 0,                       // если недоступно — 0
  "tokens_completion": 0,
  "tokens_total": 0,
  "cost_usd": 0.0,
  "subnets": ["SN13"],
  "quality_flags": []                       // например: ["too_long"]
}

7) Правила
7.1 Нормализация и дедуп (на уровне RAW)

normalize(text): lower → trim → свести повторные пробелы → убрать ведущие RT и начальный @username:; URL/хэштеги не удалять.

hash = md5(normalized_text).

Дубликаты: пропускать, если hash уже встречался за последние 7 дней (допустимо — в пределах текущего файла на MVP).

7.2 Фильтр «о Bittensor»

Отправляем в ИИ, если:

текст содержит bittensor или tao (case-insensitive), или

subnets[] не пуст, или

найдено совпадение по алиасам из data/aliases.json.

7.3 Стиль кандидата твита (выход)

≤ 280 символов.

#Bittensor обязателен.

Если есть сабсети → в конце (SN13, SN1).

Без выдуманных фактов — только из входного текста.

8) Офсеты и инкрементальное чтение

Для каждого входного JSONL ведём рядом файл *.offset (позиция в байтах).

Downstream (pipeline) читает только новые строки, после успешной обработки атомарно обновляет offset.

При падении безопасно стартуем с последнего сохранённого offset (идемпотентность).

9) Секреты и окружение

Файл .env: OPENAI_API_KEY=...

Python-пакеты: openai, python-dotenv (+ по желанию orjson).

Логи: logs/pipeline.log (INFO/ERROR с таймштампами).

10) Роли (только технические + координатор)

Координатор (Иви): держу общий контекст, свожу ответы экспертов, проверяю стыковки, даю следующий шаг.

Data / Scraping: запись в RAW JSONL, дедуп, теггинг сабсетей.

NLP / Prompt: промпт и код генерации make_tweet(...).

Backend / Pipeline: чтение RAW по офсетам → вызов OpenAI → запись CANDIDATES.

MLOps / DevOps: .env, запуск локально/VPS, расписание, логи.

11) Шаблон handoff (вставлять в конце ответов экспертов)

[HANDOFF]
Inputs: (что получил)
What I did: (коротко, 2–4 строки)
Outputs: (артефакты + пути/ссылки)
Decisions: (ключевые решения и почему)
Next: (кто следующий, что сделать, к какому сроку)
Risks/Blocks: (если есть)

12) Следующие шаги (в этом порядке)

Data / Scraping: дописать RAW JSONL + теггинг по aliases.json, выдать примеры 2–3 строк.

NLP / Prompt: файл ai/summarize.py + PROMPT_TWEET, показать пример вход→выход.

Backend / Pipeline: read_incremental.py и run_once.py, которые читают RAW и пишут CANDIDATES.

DevOps: requirements.txt, .env.example, scripts/run_local.sh, запуск по cron/systemd.

13) Примечания

data/aliases.json можно начать с {} и наполнять по мере работы.

Публикация в X — ручная (на уровне MVP). Автопостинг добавим позже отдельным этапом.

Если что-то непонятно — эскалируй координатору (Иви).
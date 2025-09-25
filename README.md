Football Analytics Platform

*Project Overview*
This is a data analytics firm specializing in football/soccer data analysis. We provide insights to clubs, leagues, and betting companies by analyzing player performance, team statistics, match outcomes, and betting patterns using European football data.

📊 Database Schema
Entity-Relationship Diagram
<img width="974" height="645" alt="image" src="https://github.com/user-attachments/assets/f0014bad-09a5-43cf-be48-7f57ba920604" />


*Структура базы данных*

Проект использует комплексную футбольную базу данных с 7 основными таблицами:

Country (11 стран)

League (11 лиг)

Team (299 команд)

Player (11,060 игроков)

Match (25,979 матчей)

Player_Attributes (183,978 рейтингов игроков)

Team_Attributes (1,458 записей тактики команд)

🛠️ Инструменты и технологии

Основные технологии

База данных: PostgreSQL 12+

Язык программирования: Python 3.8+

Управление БД: PgAdmin 4


*Библиотеки Python*

python

pandas>=1.3.0        # Манипуляции и анализ данных

psycopg2-binary>=2.9.0  # Адаптер PostgreSQL для Python

sqlalchemy>=1.4.0    # SQL инструментарий и ORM

*Данные подключения к БД*

Хост: localhost

Порт: 5432

База данных: data visualization

Пользователь: postgres

Пароль: 0000

📁 Структура проекта

text

football-analytics-project/

│

├── README.md                 # Документация проекта

├── main.py                  # Главный скрипт анализа на Python

├── queries.sql              # Коллекция SQL запросов

├── requirements.txt         # Зависимости Python

├── .gitignore              # Правила для Git

│

├── images/

│   └── er_diagram.png      # Визуальная схема БД

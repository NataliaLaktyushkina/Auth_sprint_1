Адрес репозитория:
https://github.com/NataliaLaktyushkina/Auth_sprint_1

Запуск приложения:
`docker-compose up --build`

`alembic revision -m "initial"`
`alembic revision --autogenerate`

Запуск тестов:
`docker-compose -f  'docker-compose testing.yml' up --build`


Создание пользователя с админскими правами:
Переменные окружения:
- SUPERUSER_NAME
- SUPERUSER_PASS

Команды:
- `export FLASK_APP=auth_app`
- `flask create-superuser`

[Список переменных окружения](flask_app/src/utils/.env.example)

[Документация по AuthAPI](http://127.0.0.1:80/apidocs )

##API Личный Кабинет:

### **/signup**:
- в запросе приходят логин и пароль
- проверяем, что такого пользователя в БД нет
- создаем нового пользователя
- отправляем access и refresh токены
- refresh-токены добавляем в psql с привязкой к пользователю

### **/login**:
- в запросе логин и пароль
- проверка логина и пароля. 
- Если успешно, создание access и  refresh-токенов для пользователя.
- refresh-токены добавляем в psql с привязкой к пользователю
- создание записи в таблице LoginHistory

### **/logout**:
- в запросе либо access, либо refresh токен
- токены помещаются в блэк-лист (redis) на время их жизни

### **/refresh**:
- в запросе приходит refresh-токен
- проверяем по хранилищу (redis), что пользователь в токене и пользоваель в БД идентичны
- отправляем _новые_ access и refresh-токены

### **/change_login**:
- в запросе access-токен и новый логин
- проверка, что такого логина в БД нет
- изменение логина в БД 
- отправка новых токенов (так как токены завязаны на имя пользователя)
- обновляем refresh-токен в БД

### **/change_password**:
- в запросе access-токен и новый пароль
- берем пользователя по токену
- находим пользователя в БД (для последующего обновления refresh токена)
- изменение пароля в БД 
- отправка новых токенов (изменился пароль - нужно обновить access токен)
- обновляем refresh-токен в БД

### **/login_history**:
- проверка access-токена
- выдача последних 10 входов


## Роли
### Postgres tables:
1. Roles - id, name
2. UsersRoles 

### endpoints:
###/create_role  
post  проверка прав- менеджер либо админ
### /delete_role 
delete проверка прав-менеджер либо админ 
### /change_role 
put проверка прав - менеджер либо админ
### /roles_list 
get проверка прав - менеджер либо админ

Проверка прав через токен, в который записываем роли.

## Роли пользователя:
users_roles - список ролей пользователя
assign_role - присвоение роли пользователя
detach_role - отбираем роль у пользователя

##Storage:
для блэк-листа и хранения refresh-токенов.
В текущем API используется Redis
____
# Проектная работа 6 спринта

С этого модуля вы больше не будете получать чётко расписанное ТЗ, а задания для каждого спринта вы найдёте внутри уроков. Перед тем как начать программировать, вам предстоит продумать архитектуру решения, декомпозировать задачи и распределить их между командой.

В первом спринте модуля вы напишете основу вашего сервиса и реализуете все базовые требования к нему. Старайтесь избегать ситуаций, в которых один из ваших коллег сидит без дела. Для этого вам придётся составлять задачи, которые можно выполнить параллельно и выбрать единый стиль написания кода.

К концу спринта у вас должен получиться сервис авторизации с системой ролей, написанный на Flask с использованием gevent. Первый шаг к этому — проработать и описать архитектуру вашего сервиса. Это значит, что перед тем, как приступить к разработке, нужно составить план действий: из чего будет состоять сервис, каким будет его API, какие хранилища он будет использовать и какой будет его схема данных. Описание нужно сдать на проверку. Вам предстоит выбрать, какой метод организации доступов использовать для онлайн-кинотеатра, и систему прав, которая позволит ограничить доступ к ресурсам. 

Для описания API рекомендуем использовать [OpenAPI](https://editor.swagger.io){target="_blank"}, если вы выберете путь REST. Или используйте текстовое описание, если вы планируете использовать gRPC. С этими инструментами вы познакомились в предыдущих модулях. Обязательно продумайте и опишите обработку ошибок. Например, как отреагирует ваш API, если обратиться к нему с истёкшим токеном? Будет ли отличаться ответ API, если передать ему токен с неверной подписью? А если имя пользователя уже занято? Документация вашего API должна включать не только ответы сервера при успешном завершении запроса, но и понятное описание возможных ответов с ошибкой.

После прохождения ревью вы можете приступать к программированию. 

Для успешного завершения первой части модуля в вашем сервисе должны быть реализованы API для аутентификации и система управления ролями. Роли понадобятся, чтобы ограничить доступ к некоторым категориям фильмов. Например, «Фильмы, выпущенные менее 3 лет назад» могут просматривать только пользователи из группы 'subscribers'.  

## API для сайта и личного кабинета

- [x] регистрация пользователя;
- [x] вход пользователя в аккаунт (обмен логина и пароля на пару токенов: JWT-access токен и refresh токен); 
- [x] обновление access-токена;
- [x] выход пользователя из аккаунта;
- [x] изменение логина или пароля (с отправкой email вы познакомитесь в следующих модулях, поэтому пока ваш сервис должен позволять изменять личные данные без дополнительных подтверждений);
- [x] получение пользователем своей истории входов в аккаунт;

## API для управления доступами

- CRUD для управления ролями:
  - создание роли,
  - удаление роли,
  - изменение роли,
  - просмотр всех ролей.
- назначить пользователю роль;
- отобрать у пользователя роль;
- метод для проверки наличия прав у пользователя. 

## Подсказки

1. Продумайте, что делать с анонимными пользователями, которым доступно всё, что не запрещено отдельными правами.
2. Метод проверки авторизации будет всегда нужен пользователям. Ходить каждый раз в БД — не очень хорошая идея. Подумайте, как улучшить производительность системы.
3. Добавьте консольную команду для создания суперпользователя, которому всегда разрешено делать все действия в системе.
4. Чтобы упростить себе жизнь с настройкой суперпользователя, продумайте, как сделать так, чтобы при авторизации ему всегда отдавался успех при всех запросах.
5. Для реализации ограничения по фильмам подумайте о присвоении им какой-либо метки. Это потребует небольшой доработки ETL-процесса.


## Дополнительное задание

Реализуйте кнопку «Выйти из остальных аккаунтов», не прибегая к хранению в БД активных access-токенов.

## Напоминаем о требованиях к качеству

Перед тем как сдать ваш код на проверку, убедитесь, что 

- Код написан по правилам pep8: при запуске [линтера](https://semakin.dev/2020/05/python_linters/){target="_blank"} в консоли не появляется предупреждений и возмущений;
- Все ключевые методы покрыты тестами: каждый ответ каждой ручки API и важная бизнес-логика тщательно проверены;
- У тестов есть понятное описание, что именно проверяется внутри. Используйте [pep257](https://www.python.org/dev/peps/pep-0257/){target="_blank"}; 
- Заполните README.md так, чтобы по нему можно было легко познакомиться с вашим проектом. Добавьте короткое, но ёмкое описание проекта. По пунктам опишите как запустить приложения с нуля, перечислив полезные команды. Упомяните людей, которые занимаются проектом и их роли. Ведите changelog: описывайте, что именно из задания модуля уже реализовано в вашем сервисе и пополняйте список по мере развития.
- Вы воспользовались лучшими практиками описания конфигурации приложений из урока. 

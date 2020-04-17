# Rest API для BrokFucker (08.03.2020)

## Общая информация
* Адрес сайта (пока что, локальный): **https://127.0.0.1:5000/api/v1/**
* Все запросы возвращают JSON.

## HTTP Return Codes

* HTTP `4XX` возвращается при не правильном запросе;
  ошибка на стороне отправителя.
* HTTP `429` возвращается в случае, если превышено количество запросов.
* HTTP `418` возвращается в случае, когда ip адресс получил бан, после того как продолжил отправлять запросы после кода `429`.
* HTTP `5XX` возвращается в случае, если ошибка находится на серверной стороне.

## Error Codes
* Почти все запросы могут завершиться ошибкой:

Пример ошибки:
```javascript
{
  "code": -1121,
  "msg": "Invalid symbol."
}
```
* Описание всех ошибок лежит в отдельном файле: [Errors Codes](./errors.md).

## Общая информация по запросам
* Все параметры отправляются  `query string` with content type `application/json`.
* Запросы, не требующие параметров, не обрабатывают входящие данные.
* Параметры могут находиться в любом порядке.

## Примеры запросов
* Пример запроса используя коммандную стоку Windows и `curl`.

### Пример для POST register
* **request json:** {'email': 'test@gmail.com', 'password': 'qwerty1312'}

* **curl command:**

    ```
    [windows] curl -i -H "Content-Type: application/json" -X POST -d "{""email"":""test@gmail.com"", ""password"":""qwerty1312""}"  http://127.0.0.1:5000/api/v1/register
    ```

Заметьте, что реальное тело запроса - `'{"email":"test@gmail.com", "password":"qwerty1312"}'`.

Стандартная консоль Windows (в отличии от Bash), использует только двойные ковычки для указания строки, 
а символ " внутри строки должен экранироваться еще одной ковычкой.

### Example for GET /api/v1/getUserData with authentification

Некоторые запросы требуют аутентификации.

Для этого, требуется переслать данные логина и пароля в шапке запроса.

Существует несколько уровней доступа запроса: **public**, **user**, **moderator** и **administrator**.

В случае отсутствия необходимого уровня доступа, в ответе вернется ошибка.

* **request json:** NONE

* **curl command:**

    ```
    [windows] curl -u test@gmail.com:qwerty1312 -i http://localhost:5000/api/v1/getUserData
    ```

  
# Список всех запросов
## Публичные запросы
* ```(public) GET /api/v1/ping```
  * [Проверяет соединение с сервером.](#Проверка-соединения)

## Запросы регистрации
* ```(public) POST /api/v1/register```
  * [Начинает процесс регистрации нового пользователя.](#Создать-новый-аккаунт)
* ```(public) GET /api/v1/register/verify/<string:verification_hash>```
  * [Подтверждает регистрацию.](#Подтвердить-регистрацию)

## Запросы пользователя
### Данные
* ```(user) GET /api/v1/user```
  * [Информация о текущем пользователе.](#Информация-о-текущем-пользователе)
* ```(user) PUT /api/v1/user```
  * [Обновить данные текущего пользователя.]()
* ```(user) PUT /api/v1/user/password```
  * [Запрос на изменение пароля пользователя.]()
* ```(public) GET /api/v1/lots/password/verification/<string:code>```
  * [Подтвердить код изменения пароля.]()
* ```(user) GET /api/v1/user/restore/<string:email>```
  * [Восстановить пароль.]()
* ```(public) GET /api/v1/user/restore/verify/<string:code>```
  * [Подтвердить восстановление пароля.]()
### Аватар
* ```(user) GET /api/v1/user/avatar```
  * [Ссылка на аватар текущего пользователя.]()
* ```(user) POST /api/v1/user/avatar```
  * [Загрузить новый аватар.]()
* ```(user) DELETE /api/v1/user/avatar```
  * [Удалить текущий аватар.]()
  
## Лоты
### Общее
* ```(public) GET /api/v1/lots/settings```
  * [Информация о доступных значениях различных полей лотов.]()
* ```(public) GET /api/v1/lots```
  * [Получить все публичные лоты.]()
* ```(public) GET/POST /api/v1/lots/approved```
  * [Копия GET /api/v1/lots.]()
* ```(user) POST /api/v1/lots```
  * [Создать новый лот.]()
* ```(public) GET /api/v1/lots/<int:id>```
  * [Получить данные о лоте.]()
* ```(user) PUT /api/v1/lots/<int:id>```
  * [Обновить данные лота.]()
* ```(user) POST /api/v1/lots/<int:id>```
  * [Восстановить удаленный лот.]()
* ```(user) DELETE /api/v1/lots/<int:id>```
  * [Удалить лот.]()
* ```(user) DELETE /api/v1/lots/personal/deleted/<int:lot_id>```
  * [Полностью удалить лот.]()
* ```(public) GET /api/v1/lots/<int:id>/photos```
  * [Получить список фотографий лота.]()
* ```(user) POST /api/v1/lots/<int:id>/photos```
  * [Добавить лоту фотографию.]()
* ```(user) DELETE /api/v1/lots/<int:id>/photos/<int:photo_id>```
  * [Удалить фотографию лота.]()
### Избранное
* ```(user) PUT /api/v1/lots/favorites/<int:lot_id>```
  * [Добавить лот в избранное.]()
* ```(user) DELETE /api/v1/lots/favorites/<int:lot_id>```
  * [Удалить лот из избранных.]()
* ```(user) GET/POST /api/v1/lots/favorites```
  * [Получить список избранных лотов.]()
### Свои лоты
* ```(user) GET/POST /api/v1/lots/personal```
  * [Получить список своих не занятых лотов.]()
* ```(user) GET/POST /api/v1/lots/personal/current```
  * [Дубликат /api/v1/lots/personal]()
* ```(user) GET/POST /api/v1/lots/personal/taken```
  * [Получить список своих лотов, нашедших финансирование.]()
* ```(user) GET/POST /api/v1/lots/personal/finished```
  * [Получить список своих завершенных лотов.]()
* ```(user) GET/POST /api/v1/lots/personal/deleted```
  * [Получить список своих удаленных лотов.]()
### Подписки
* ```(user) PUT /api/v1/lots/subscription/<int:id>```
  * [Подписаться на лот.]()
* ```(user) DELETE /api/v1/lots/subscription/<int:id>```
  * [Убрать подписку на лот.]()
* ```(user) GET /api/v1/lots/subscription```
  * [Получить список лотов, на которые ты подписан.]()
### Запросы
* ```(user) PUT /api/v1/lots/personal/<int:lot_id>/request/guarantee```
  * [Запросить гарантию клуба.]()
* ```(user) PUT /api/v1/lots/personal/<int:lot_id>/request/verify_security```
  * [Запросить подтверждение обеспечения.]()

## Запросы модератора
### Лоты
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/approve```
  * [Подтвердить лот.]()
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/security```
  * [Подтвердить проверенное обеспечение лота.]()
* ```(moderator) DELETE /api/v1/lots/<int:lot_id>/security```
  * [Убрать проверенное обеспечение лота.]()
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/guarantee```
  * [Установить гарантию клуба лоту.]()
* ```(moderator) DELETE /api/v1/lots/<int:lot_id>/guarantee```
  * [Убрать гарантию клуба у лота.]()
* ```(moderator) GET /api/v1/lots/unapproved```
  * [Получить список неподтвержденных лотов.]()
### Подписки
* ```(moderator) GET /api/v1/lots/subscription/approved```
  * [Получить список подтвержденных подписок.]()
* ```(moderator) GET /api/v1/lots/subscription/unapproved```
  * [Получить список неподтвержденных подписок.]()
* ```(moderator) DELETE /api/v1/lots/unapproved/<int:lot_id>```
  * [Отклонить неподтвержденный лот.]()
### Запросы
* ```(moderator) GET /api/v1/lots/requested/guarantee```
  * [Получить список лотов, запросивших гарантию клуба.]()
* ```(moderator) GET /api/v1/lots/requested/security_verification```
  * [Получить список лотов, запросивших проверку обеспечения.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/approve```
  * [Подтвердить неподтвержденную подписку.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/unapprove```
  * [Снять подтверждение подписки.]()
* ```(moderator) DELETE /api/v1/lots/subscription/<string:id>```
  * [Удалить неподтвержденную подписку.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/finish```
  * [Закончить подтвержденную подписку.]()
### Архив
* ```(moderator) GET/POST /api/v1/lots/archive```
  * [Получить список архивных подписок.]()
* ```(moderator) GET /api/v1/lots/archive/<int:lot_id>```
  * [Посмотреть историю архивной подписки.]()

## Запросы администратора
* ```(administrator) PUT /api/v1/user/<string:email>/moderator```
  * [Добавить права модератора.]()
* ```(administrator) DELETE /api/v1/user/<string:email>/moderator```
  * [Убрать права модератора.]()

# Данные о запросах
## Публичные запросы
### Проверка соединения
```
GET /api/v1/ping
```
**Описание:**

Проверяет соединение с Rest API.
Возвращает простое сообщение "pong".

**Уровень доступа:**

Public

**Параметры:**

Отсутствуют

**Вес:** 

1

**Ответ:**
```javascript
{
  "msg": "pong"
}
```

## Запросы регистрации
### Создать новый аккаунт
```
POST /api/v1/register
```
**Описание:**

Запрос на создание нового аккаунта. 
Отправит письмо с подтверждением на почту, если такая почта существует. 
Иначе, выдаст ошибку.
В письме с подтверждением будет ссылка, перейдя по которой 
браузер отправит запрос на подтверждение почты с кодом из сообщения.

**Уровень доступа:**

Public

**Параметры:**
* email: string | обязательный
* password: string | обязательный

**Вес:** 

10

**Ответ:**
```javascript
{
  'msg': 'Verification is sent to {email}'
}
```

### Подтвердить регистрацию
```
GET /api/v1/register/verify/<string:verification_hash>
```
**Описание:**

Подтверждает регистрацию по коду {verification_hash}.
Ссылка с этим кодом присылается на почту пользователю:
./email_verification.html?code={verification_hash}

При желании, эту ссылку можно изменить в настройках сервера, 
в файле settings.json, в параметре "email_verification_link_base".

**Уровень доступа:**

Public

**Параметры:**

Отсутствуют

**Ответ:**
```javascript
{
  'msg': 'Email was succesfully confirmed.'
}
```

## Запросы пользователя
### Информация о текущем пользователе
```
GET /api/v1/user
```
**Описание:**

Возвращает словарь с данными о текущем пользователе.

**Уровень доступа:**

User

**Параметры:**

Отсутствуют

**Вес:** 

1

**Ответ:**
```javascript
{
  "avatar":"http://127.0.0.1:5000/image/user/default.jpg",
  "email":"example@gmail.com",
  "name":"Head Admin",
  "phone_number":null,
  "registration_date":"2020-02-24 00:50:24.262170",
  "type":"admin"
}

```

### Обновить данные текущего пользователя
```
PUT /api/v1/user
```
**Описание:**

Изменить параметры пользователя, такие как
номер телефона и/или имя.

**Уровень доступа:**

User

**Параметры:**
* phone: string
* name: string

**Вес:** 

2

**Ответ:**
```javascript
{
  "msg": "Data is edited successfully."
}
```

### Краткое описание
```
PUT /api/v1/user/password
```
**Описание:**

Отправляет запрос на изменение пароля.
Подтверждение прийдет на почту пользователя с ссылкой,
по аналогии с подтверждением почты.

**Уровень доступа:**

User

**Параметры:**

* password: string | обязательный

**Вес:** 

10

**Ответ:**
```javascript
{

}
```

* ```(user) PUT /api/v1/user/password```
  * [Запрос на изменение пароля пользователя.]()
* ```(public) GET /api/v1/lots/password/verification/<string:code>```
  * [Подтвердить код изменения пароля.]()
* ```(user) GET /api/v1/user/restore/<string:email>```
  * [Восстановить пароль.]()
* ```(public) GET /api/v1/user/restore/verify/<string:code>```
  * [Подтвердить восстановление пароля.]()
### Аватар
* ```(user) GET /api/v1/user/avatar```
  * [Ссылка на аватар текущего пользователя.]()
* ```(user) POST /api/v1/user/avatar```
  * [Загрузить новый аватар.]()
* ```(user) DELETE /api/v1/user/avatar```
  * [Удалить текущий аватар.]()
  
## Лоты
### Общее
* ```(public) GET /api/v1/lots/settings```
  * [Информация о доступных значениях различных полей лотов.]()
* ```(public) GET /api/v1/lots```
  * [Получить все публичные лоты.]()
* ```(public) GET/POST /api/v1/lots/approved```
  * [Копия GET /api/v1/lots.]()
* ```(user) POST /api/v1/lots```
  * [Создать новый лот.]()
* ```(public) GET /api/v1/lots/<int:id>```
  * [Получить данные о лоте.]()
* ```(user) PUT /api/v1/lots/<int:id>```
  * [Обновить данные лота.]()
* ```(user) POST /api/v1/lots/<int:id>```
  * [Восстановить удаленный лот.]()
* ```(user) DELETE /api/v1/lots/<int:id>```
  * [Удалить лот.]()
* ```(user) DELETE /api/v1/lots/personal/deleted/<int:lot_id>```
  * [Полностью удалить лот.]()
* ```(public) GET /api/v1/lots/<int:id>/photos```
  * [Получить список фотографий лота.]()
* ```(user) POST /api/v1/lots/<int:id>/photos```
  * [Добавить лоту фотографию.]()
* ```(user) DELETE /api/v1/lots/<int:id>/photos/<int:photo_id>```
  * [Удалить фотографию лота.]()
### Избранное
* ```(user) PUT /api/v1/lots/favorites/<int:lot_id>```
  * [Добавить лот в избранное.]()
* ```(user) DELETE /api/v1/lots/favorites/<int:lot_id>```
  * [Удалить лот из избранных.]()
* ```(user) GET/POST /api/v1/lots/favorites```
  * [Получить список избранных лотов.]()
### Свои лоты
* ```(user) GET/POST /api/v1/lots/personal```
  * [Получить список своих не занятых лотов.]()
* ```(user) GET/POST /api/v1/lots/personal/current```
  * [Дубликат /api/v1/lots/personal]()
* ```(user) GET/POST /api/v1/lots/personal/taken```
  * [Получить список своих лотов, нашедших финансирование.]()
* ```(user) GET/POST /api/v1/lots/personal/finished```
  * [Получить список своих завершенных лотов.]()
* ```(user) GET/POST /api/v1/lots/personal/deleted```
  * [Получить список своих удаленных лотов.]()
### Подписки
* ```(user) PUT /api/v1/lots/subscription/<int:id>```
  * [Подписаться на лот.]()
* ```(user) DELETE /api/v1/lots/subscription/<int:id>```
  * [Убрать подписку на лот.]()
* ```(user) GET /api/v1/lots/subscription```
  * [Получить список лотов, на которые ты подписан.]()
### Запросы
* ```(user) PUT /api/v1/lots/personal/<int:lot_id>/request/guarantee```
  * [Запросить гарантию клуба.]()
* ```(user) PUT /api/v1/lots/personal/<int:lot_id>/request/verify_security```
  * [Запросить подтверждение обеспечения.]()

## Запросы модератора
### Лоты
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/approve```
  * [Подтвердить лот.]()
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/security```
  * [Подтвердить проверенное обеспечение лота.]()
* ```(moderator) DELETE /api/v1/lots/<int:lot_id>/security```
  * [Убрать проверенное обеспечение лота.]()
* ```(moderator) PUT /api/v1/lots/<int:lot_id>/guarantee```
  * [Установить гарантию клуба лоту.]()
* ```(moderator) DELETE /api/v1/lots/<int:lot_id>/guarantee```
  * [Убрать гарантию клуба у лота.]()
* ```(moderator) GET /api/v1/lots/unapproved```
  * [Получить список неподтвержденных лотов.]()
### Подписки
* ```(moderator) GET /api/v1/lots/subscription/approved```
  * [Получить список подтвержденных подписок.]()
* ```(moderator) GET /api/v1/lots/subscription/unapproved```
  * [Получить список неподтвержденных подписок.]()
* ```(moderator) DELETE /api/v1/lots/unapproved/<int:lot_id>```
  * [Отклонить неподтвержденный лот.]()
### Запросы
* ```(moderator) GET /api/v1/lots/requested/guarantee```
  * [Получить список лотов, запросивших гарантию клуба.]()
* ```(moderator) GET /api/v1/lots/requested/security_verification```
  * [Получить список лотов, запросивших проверку обеспечения.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/approve```
  * [Подтвердить неподтвержденную подписку.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/unapprove```
  * [Снять подтверждение подписки.]()
* ```(moderator) DELETE /api/v1/lots/subscription/<string:id>```
  * [Удалить неподтвержденную подписку.]()
* ```(moderator) GET /api/v1/lots/subscription/<string:id>/finish```
  * [Закончить подтвержденную подписку.]()
### Архив
* ```(moderator) GET/POST /api/v1/lots/archive```
  * [Получить список архивных подписок.]()
* ```(moderator) GET /api/v1/lots/archive/<int:lot_id>```
  * [Посмотреть историю архивной подписки.]()

## Запросы администратора
* ```(administrator) PUT /api/v1/user/<string:email>/moderator```
  * [Добавить права модератора.]()
* ```(administrator) DELETE /api/v1/user/<string:email>/moderator```
  * [Убрать права модератора.]()


### Краткое описание
```
POST /api/v1/register
```
**Описание:**

Конкретное описание

**Уровень доступа:**

Public/User/Moderator/Administrator

**Параметры:**

Отсутствуют

**Вес:** 

10

**Ответ:**
```javascript
{

}
```
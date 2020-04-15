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

Существует несколько уровней доступа запроса: **Public**, **User**, **Moderator** и **Admin**.

В случае отсутствия необходимого уровня доступа, в ответе вернется ошибка.

* **request json:** NONE

* **curl command:**

    ```
    [windows] curl -u test@gmail.com:qwerty1312 -i http://localhost:5000/api/v1/getUserData
    ```

  
# Список всех запросов
## Публичные запросы
* (public) ```GET /api/v1/ping```
  * [Проверяет соединение с сервером.](#Проверка-соединения)

## Запросы регистрации
* ```(public) POST /api/v1/register```
  * [Начинает процесс регистрации нового пользователя.](#Создать-новый-аккаунт)
* ```(public) GET /api/v1/register/verify/<string:verification_hash>```
  * [Подтверждает регистрацию.](#Подтвердить-регистрацию)

## Запросы пользователя
### Данные
* ```(user) GET /api/v1/user```
  * [Информация о текущем пользователе.]()
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

-------------------------------------------------------------

Документация далее нуждается в доработке и русском переводе.

Не рекомендуется ее читать, так как некоторые вещи могут быть не верными или устаревшими.

# Данные о запросах
## Публичные запросы

### Проверка соединения
```
GET /api/v1/ping
```
Проверяет соединение с Rest API.

**Уровень доступа:**
Public

**Параметры:**
* NONE

**Ответ:**
```javascript
{}
```

### Создать новый аккаунт
```
POST /api/v1/register
```
Запрос на создание нового аккаунта. Отправит письмо на почту.

**Уровень доступа:**
Public

**Параметры:**
* email: string
* password: string

**Ответ:**
```javascript
{
  'msg': 'New user created'
}
```

### Подтвердить регистрацию
```
POST /api/v1/register
```
Запрос на создание нового аккаунта. Отправит письмо на почту.

**Уровень доступа:**
Public

**Параметры:**
* email: string
* password: string

**Ответ:**
```javascript
{
  'msg': 'New user created'
}
```

## Запросы польщователя

### Get user data
```
GET /api/v1/user
```
Load all main user data.

**Level:**
User

**Parameters:**
* NONE

**Response:**
```javascript
{
  'email': 'test@gmail.com',
  'type': 'user',
  'registration_date': '',
  'name': null,
  'phone_number': null,
  'avatar': 'http://127.0.0.1:5000/image/user/diawyd8i1u82dy182hdh.png'
}
```

### Create new lot
```
POST /api/v1/lots/createNew
```
The new lot will be by default unapproved and will wait for moderator to approve.

**Level:**
User

**Parameters:**
* name: string
* amount: int
* currency: string
* term: int
* return_way: int
* security: string
* percentage: double
* form: int

**Response:**
```javascript
{
  'msg': 'New lot created'
}
```

### Get list of approved lots
```
GET /api/v1/lots/approved
```
The list of dictionaries will return.

**Level:**
User

**Parameters:**
* NONE

**Response:**
```javascript
[
  {
    'id': 1,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  {
    'id': 2,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  ...,
  {
    'id': 3000,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
]
```

### Get favorite lots list
```
GET /api/v1/lots/favorites
```
Returns the list of all user's favorite lots.

**Level:**
User

**Parameters:**
* NONE

**Response:**
```javascript
[
  {
    'id': 1,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  {
    'id': 2,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  ...,
  {
    'id': 3000,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
]
```

### Add lot to favorites
```
POST /api/v1/lots/favorites/<lot_id>

or

PUT /api/v1/lots/favorites/<lot_id>
```
A lot id parametr should me passed at `<lot_id>` place.

**Level:**
User

**Parameters:**
* NONE

**Response:**
```javascript
{
  'msg': 'A lot is added to favorites'
}
```

### Remove lot from favorites
```
DELETE /api/v1/lots/favorites/<lot_id>
```
A lot id parametr should me passed at `<lot_id>` place.

**Level:**
User

**Parameters:**
* NONE

**Response:**
```javascript
{
  'msg': 'A lot is removed from favorites'
}
```

## Moderator endpoints

### Approve a lot
```
PUT /api/v1/lots/<int:lot_id>/approve
```
A lot id parametr should me passed at `<lot_id>` place.

**Level:**
Moderator

**Parameters:**
* NONE

**Response:**
```javascript
{
  'msg': 'A lot is now approved'
}
```

### Set lot's security checked
```
PUT /api/v1/lots/<int:lot_id>/setSecurityChecked
```
A lot id parametr should me passed at `<lot_id>` place.

**Level:**
Moderator

**Parameters:**
* NONE

**Response:**
```javascript
{
  'msg': 'Lot\'s security is now checked'
}
```

### Set lot's security unchecked
```
PUT /api/v1/lots/<int:lot_id>/setSecurityUnchecked
```
A lot id parametr should me passed at `<lot_id>` place.

**Level:**
Moderator

**Parameters:**
* NONE

**Response:**
```javascript
{
  'msg': 'Lot\'s security is no more checked'
}
```

### Get all unapproved lots
```
GET /api/v1/lots/unapproved
```
Returns the list of unapproved lots.

**Level:**
Moderator

**Parameters:**
* NONE

**Response:**
```javascript
[
  {
    'id': 1,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  {
    'id': 2,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
  ...,
  {
    'id': 3000,
    'date': 'date',
    'name': 'testname',
    'user': 'test@gmail.com',
    'amount': 12345,
    'currency': 'USD',
    'term': 0,
    'return_way': 2,
    'security': 'house',
    'percentage': 0',
    'form': 1,
    'security_checked': false,
    'guarantee_percentage': 90
  },
]
```

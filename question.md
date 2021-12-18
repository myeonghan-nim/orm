# Question

- Write the ORM statement and SQL statement to solve the following problem.

## CRUD

1. GET all users

```python
User.objects.all()
```

```sql
SELECT * FROM orm_user;
```

2. CREATE a user

```python
User.objects.create(
    first_name='길동',
    last_name='홍',
    age=30,
    country='제주특별자치도',
    phone='010-1234-1234',
    balance=100000
)
```

```sql
INSERT INTO orm_user
VALUES (101, '길동', '홍', 30, '제주특별자치도', '010-1234-1234', 100000);
```

3. GET a user

```python
User.objects.get(id=59)
```

```sql
SELECT * FROM orm_user WHERE rowid=59;
```

4. UPDATE a user

```python
user = User.objects.get(id=59)
user.age = 26
user.save()
```

```sql
UPDATE orm_user
SET age=26
WHERE id=59;
```

5. DELETE a user

```python
User.objects.get(id=59).delete()
```

```sql
DELETE orm_user WHERE id=59;
```

## Conditional sentence

1. Total number of users

```python
User.objects.count()
```

```sql
SELECT COUNT(*) FROM orm_user;
```

2. Name of users who age is 30

```python
User.objects.filter(age=30).values('first_name')
```

```sql
SELECT first_name FROM orm_user WHERE age=30;
```

3. Number of users who age is over 30

```python
User.objects.filter(age__gte=30).count()
```

```sql
SELECT COUNT(*) FROM orm_user WHERE age>=30;
```

4. Number of users who age is 30 and last name is Kim

```python
User.objects.filter(age=30, last_name='김').count()
```

```sql
SELECT COUNT(*) FROM orm_user
WHERE age=30 AND last_name='김';
```

5. Number of users who phone number starts with 02

```python
User.objects.filter(phone__startswith='02-').count()
```

```sql
SELECT COUNT(*) FROM orm_user
WHERE phone LIKE '02-%';
```

6. Name of users who lives in Gangwon-do and last name is Hwang

```python
User.objects.filter(country='강원도', last_name='황')[0].first_name
```

```sql
SELECT first_name FROM orm_user
WHERE country='강원도' AND last_name='황';
```

## Sort

1. 10 in the order of age

```python
User.objects.order_by('-age')[:10].values()
```

```sql
SELECT * FROM orm_user ORDER BY age DESC LIMIT 10;
```

2. 10 in the order of small balance

```python
User.objects.order_by('balance')[:10].values()
```

```sql
SELECT * FROM orm_user ORDER BY balance ASC LIMIT 10;
```

3. 5th people in the order of last name and first name

```python
User.objects.order_by('-last_name', '-first_name')[4]
```

```sql
SELECT * FROM orm_user
ORDER BY last_name DESC, first_name DESC
LIMIT 1 OFFSET 4;
```

## Expression

- Enter the code below in python shell to use expression.

`from django.db.models import Avg, Min, Max, Sum`

1. Average age

```python
User.objects.aggregate(Avg('age'))
```

```sql
SELECT AVG(age) FROM orm_user;
```

2. Average age who last name is Kim

```python
User.objects.filter(last_name='김').aggregate(Avg('age'))
```

```sql
SELECT AVG(age) FROM orm_user WHERE last_name='김';
```

3. Max balance

```python
User.objects.aggregate(Max('balance'))
```

```sql
SELECT MAX(balance) FROM orm_user;
```

4. Total balance

```python
User.objects.aggregate(Sum('balance'))
```

```sql
SELECT SUM(balance) FROM orm_user;
```

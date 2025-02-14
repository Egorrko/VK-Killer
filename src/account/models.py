from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .services import avatar


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password):
        user = self.model(email=email,
                          username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email,
                                password=password,
                                username=username)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(upload_to='avatars')
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def save(self, *args, **kwargs):
        if not self.avatar:
            # если у пользователя нет аватарки - сгенерировать и сохранить
            self.avatar = 'avatars/defaults/' + avatar.create(self.username)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Friend(models.Model):
    users = models.ManyToManyField(Account, related_name='users')
    users_accepted = models.ManyToManyField(Account, related_name='users_accepted')


class Dm(models.Model):
    users = models.ManyToManyField(Account)


class Message(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    dm = models.ForeignKey(Dm, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.message

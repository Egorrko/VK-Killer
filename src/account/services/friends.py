from random import sample
from account.models import Friend, Account
from django.db.models import Q

def get(user: Account, only_accepted: bool) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    return Friend.objects.filter()
    users = []
    for fr in Friend.objects.filter(users=user).exclude(users__users_accepted__exact=user):
        for usr in fr.users_accepted.filter()
            if usr != user and len(fr.users_accepted.all()) > (1 if only_accepted else 0):
                users.append(usr)
    return users


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = get(user, True)
    if len(users) < k: k = len(users)
    return sample(users, k=k), len(users)



def get_account(id: int):
    db.get(id)

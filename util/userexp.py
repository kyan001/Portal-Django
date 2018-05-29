from main.models import UserExp


def addExp(user, category, incr, operation):
    """add exp to user's category

    Args:
        user: who will increase the exp
        category: which category should the exp added to
        incr: int, how much should the exp added
        operation: the description of the add exp operation, will save to ExpHistory
    """
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category=category)
    userexp.add(incr, operation)

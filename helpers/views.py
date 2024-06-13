from django.shortcuts import render
import random


# 404 page not found error
def handle_not_found(request, exception):
    return render(request, 'not-found.html')


# 500 server error 
def handle_server_error(request):
    return render(request, 'server-error.html')


def create_acc_no():
    l = [34, 78, 90, 45, 89, 27, 91]
    l = random.choice(l)
    r = random.randint(110000001, 999999999)
    k = str(l) + str(r)
    return k


def create_ref():
    l = ['af45', '9rt', 'vb', 'tm7', 'x8k', 'pl', 'wr3']
    l = random.choice(l)
    r = random.randint(1100000000000, 9999999999999)
    k = str(l) + str(r)
    return k
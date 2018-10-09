import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from .forms import ContactForm


from .util.helper import get_all_claim_title_id, get_claim_given_id
file_names = {
    "iDebate": '../data/idebate/idebate.json'
}

"""Helper functions"""
def load_json(file_name):
    with open(file_name, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        return data

def get_json(request):
    data = load_json(file_names["iDebate"])
    return JsonResponse({"data": data})


def get_pool_from_claim_id(claim_id):
    """
    TODO: Change this function! Right now it's only for testing purpose
    :param claim_id: id of the claim
    :return:
    """
    related_persp_anno = PerspectiveRelation.objects.filter(author=PerspectiveRelation.GOLD, claim_id=claim_id).\
        order_by("?")[:2]
    related_persps = [Perspective.objects.get(id=rel.perspective_id) for rel in related_persp_anno]

    return related_persps


def get_all_persp(claim_id):
    """
    :param claim_id: id of the claim
    :return: list of perspectives
    """
    related_persp_anno = PerspectiveRelation.objects.filter(author=PerspectiveRelation.GOLD, claim_id=claim_id).\
        order_by("?")
    related_persps = [Perspective.objects.get(id=rel.perspective_id) for rel in related_persp_anno]

    return related_persps


""" APIs """
@login_required
def main_page(request):
    context = {
        "datasets": list(file_names.keys())
    }
    return render(request, 'main.html', context)


@login_required
def vis_claims(request):
    data = load_json(file_names["iDebate"])
    claim_titles = get_all_claim_title_id(data)

    # print(len(claim_titles))
    context = {
        "claim_titles": claim_titles
    }
    return render(request, 'claims.html', context)


@login_required
def vis_persps(request, claim_id):
    data = load_json(file_names["iDebate"])
    claim = get_claim_given_id(data, claim_id)
    context = {
        "claim": claim
    }

    return render(request, 'persp.html', context)


@login_required
def vis_neg_anno(request, claim_id):
    return render(request, 'claim_neg_anno.html', {})


@login_required
def vis_relation(request, claim_id):
    try:
        claim = Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        pass  # TODO: Do something? 404?

    perspective_pool = get_pool_from_claim_id(claim_id)

    return render(request, 'claim_relation.html', {
        "claim": "",
        "perspective_pool": perspective_pool
    })

@login_required
def submit_rel_anno(request):
    """
    Accepts POST requests and update the annotations
    """
    if request.method != 'POST':
        raise ValueError("submit_rel_anno API only supports POST request")
        # TODO: Actaully not sure what to do here..
    else:
        claim_id = request.POST.get('claim_id')
        annos = request.POST.getlist('annotations[]')
        if claim_id and annos:
            for a in annos:
                parts = a.split(',')
                if len(parts) != 2:
                    return HttpResponse("Submission Failed! Annotation not valid.", status=400)

                persp_id = parts[0]
                rel = parts[1]
                print(persp_id, rel)
                anno_entry = PerspectiveRelation.objects.create(author="TEST", claim_id=claim_id, perspective_id=persp_id, rel=rel)
                anno_entry.save()

        else:
            return HttpResponse("Submission Failed! Annotation not valid.", status=400)

        return HttpResponse("Submission Success!", status=200)


def render_login_page(request):
    """
    Renderer for login page
    """
    return render(request, "login.html", {})

def render_list_page(request):
    """
    Renderer the list of task
    """

    isin_db = False
    if True: # TODO: change this condition to: if the table has been created for the user
        isin_db = True

    ## TODO: load up the task list from DB
    task_list = [
        {
            "id": 2,
            "done": False
        },
        {
            "id": 3,
            "done": False
        },
        {
            "id": 4,
            "done": True
        },
        {
            "id": 5,
            "done": False
        }
    ]

    tasks_are_done = all(item["done"] for item in task_list)

    task_id = 0
    if tasks_are_done:  # TODO: change this condition to if the user has completed the task
        task_id = 67542

    context = {"task_id": task_id, "isin_db": isin_db, "task_list": task_list}

    return render(request, "list_tasks.html", context)

def render_instructions(request):
    return render(request, "instructions.html", {})

def render_contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ['danyal.khashabi@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "contact.html", {'form': form})

def successView(request):
    return HttpResponse('Success! Thank you for your message.')

@login_required
def vis_normalize_persp(request, claim_id):
    try:
        claim = Claim.objects.get(id=claim_id)
    except Claim.DoesNotExist:
        pass  # TODO: Do something? 404?

    perspective_pool = get_all_persp(claim_id)

    return render(request, 'normalize_persp.html', {
        "claim": claim,
        "perspective_pool": perspective_pool
    })

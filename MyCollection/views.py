import json

from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.contrib.auth.hashers import check_password

from MyCollection.models import Record, Group, Order, User
from MyCollection.file_utilities import (get_group_thumbnail,
                                         get_group_list,
                                         get_unassigned_records_count,
                                         get_unassigned_records_list)
from MyCollection.forms import AddGroupForm, EditGroupForm, EditRecordForm


def index(request):
    user_id = request.user.id
    if user_id is None:
        return HttpResponseRedirect('/accounts/login/')
    groups = Group.objects.filter(user_id=user_id).order_by('group_order').select_related().annotate(
        num_recs=Count('records'))
    group_count = len(groups)
    records = Record.objects.filter(user_id=user_id).order_by('-date_added')[:30]
    non_group_record_count = get_unassigned_records_count(user_id)
    thumbs = get_group_thumbnail(groups)
    context = {
        'groups': thumbs,
        'group_count': group_count,
        'records': records,
        'AddGroupForm': AddGroupForm(),
        'non_group_record_count': non_group_record_count,
    }
    return render(request, "MyCollection/index.html", context)


def group(request, group_id):
    user_id = request.user.id
    non_group_record_count = get_unassigned_records_count(user_id)
    if group_id == '0':
        records = get_unassigned_records_list(user_id)
        group_data = {}
        group_local = {'name': 'Unassigned records'}
    else:
        group_local = Group.objects.get(pk=group_id)
        user = group_local.user_id
        # print(user)
        if user_id != user:
            return HttpResponseRedirect('/accounts/login/')
        group_data = {
            'id': group_local.id,
            'name': group_local.name,
            'introduction': group_local.introduction,
            'public_display': group_local.public_display,
        }
        records = Order.objects.filter(grp=group_id).select_related().order_by('number')
    groups_set = Group.objects.filter(user_id=user_id).order_by('group_order').select_related().annotate(
        num_recs=Count('records'))
    thumbs = get_group_thumbnail(groups_set)
    context = {
        'groups': thumbs,
        'group_local': group_local,
        'group_id': group_id,
        'records': records,
        'AddGroupForm': AddGroupForm(),
        'EditGroupForm': EditGroupForm(group_data),
        'non_group_record_count': non_group_record_count,
    }
    return render(request, "MyCollection/index.html", context)


def groupadd(request):
    user_id = request.user.id
    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(request.POST, user_id)
            new_group_id = new_group.id
            return_url = '/group/%s' % new_group_id
            return HttpResponseRedirect(return_url)


@csrf_exempt
def groupview(request, group_id):
    user_id = request.user.id
    group_local = Group.objects.get(pk=group_id)
    user = group_local.user_id
    if user_id != user:
        return HttpResponseRedirect('/index')
    if request.method == 'POST':
        view_value = request.POST.get('view')
        Group.objects.filter(pk=group_id).update(view=view_value)
    return HttpResponse('')


def groupedit(request, group_id):
    user_id = request.user.id
    group_local = Group.objects.get(pk=group_id)
    user = group_local.user_id
    if user_id != user:
        return HttpResponseRedirect('/index')
    if request.method == 'POST':
        form = EditGroupForm(request.POST, instance=group_local)
        if form.is_valid():
            form.save(request.POST, user_id, group_id)
            return_url = '/group/%s' % group_id
            return HttpResponseRedirect(return_url)


def groupdelete(request, group_id):
    user_id = request.user.id
    group_local = Group.objects.get(pk=group_id)
    user = group_local.user_id
    if user_id != user:
        return HttpResponseRedirect('/index')
    Group.objects.filter(pk=group_id).delete()
    return_url = '/index'
    return HttpResponseRedirect(return_url)


def groupsort(request):
    # display groups for sorting
    user_id = request.user.id
    groups_set = Group.objects.filter(user_id=user_id).order_by('group_order').select_related().annotate(
        num_recs=Count('records'))
    thumbs = get_group_thumbnail(groups_set)
    url = 'sortgroup'
    context = {
        'groups': thumbs,
        'url': url,
    }
    return render(request, "MyCollection/sort.html", context)


def recordsort(request, group_id):
    group_local = Group.objects.get(pk=group_id)
    records = Order.objects.filter(grp=group_id).select_related().order_by('number')
    url = 'sortrecord'
    context = {
        'group_id': group_id,
        'group': group_local,
        'records': records,
        'url': url,
    }
    return render(request, "MyCollection/sort.html", context)


@csrf_exempt
def sortgroup(request):
    user_id = request.user.id
    for index_str, item_id in enumerate(request.POST.getlist('item[]')):
        item = get_object_or_404(Group, id=int(str(item_id)), user_id=user_id)
        item.group_order = index_str
        item.save()
    return HttpResponse('')


@csrf_exempt
def sortrecord(request, group_id):
    for index_str, item_id in enumerate(request.POST.getlist('item[]')):
        item = get_object_or_404(Order, rec=int(str(item_id)), grp=group_id)
        item.number = index_str
        item.save()
    return HttpResponse('')


def recordview(request, record_id):
    user_id = int(request.user.id)
    record = Record.objects.filter(pk=record_id)
    user = int(record[0].user_id)
    if user_id != user:
        return HttpResponseRedirect('/index')
    data = serializers.serialize('json', record)
    return HttpResponse(data, content_type='application/json')


def recordgroup(request, record_id):
    user_id = int(request.user.id)
    data = get_group_list(record_id, user_id)
    return HttpResponse(data, content_type='text/html')


@csrf_exempt
def recordedit(request, record_id):
    user_id = int(request.user.id)
    record = Record.objects.get(pk=record_id)
    user = int(record.user_id)
    if user_id != user:
        return HttpResponseRedirect('/index')
    if request.method == 'POST':
        form = EditRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save(request.POST, user_id, record_id)
        else:
            print("invalid")
    return HttpResponse('')


@csrf_exempt
def recorddelete(request, record_id):
    user_id = request.user.id
    record = Record.objects.get(pk=record_id)
    user = record.user_id
    if user_id != user:
        return HttpResponseRedirect('/index')
    Record.objects.filter(pk=record_id).delete()
    return HttpResponse('')


@csrf_exempt
def userconfirm(request):
    setattr(request, '_dont_enforce_csrf_checks', True)
    if request.method == 'POST':
        account = request.POST.get('user')
        if account:
            request_password = request.POST.get('pwd')
            user = User.objects.get(username=account)
            user_password = user.password
            user_id = user.id
            is_user = check_password(request_password, user_password)
            if is_user:
                user_groups = Group.objects.filter(user=user_id).order_by('group_order')
                response_dict = {'user_id': user_id}
                x = 1
                for group_qs in user_groups:
                    group_combine = "%s|%s" % (group_qs.id, group_qs.name)
                    response_dict[x] = group_combine
                    x += 1
                response_string = json.dumps(response_dict)
                ct = "content_type='application/json'"
            else:
                response_string = "User not found(1)"
                ct = "content_type='text/plain'"
        else:
            response_string = "User not found(2)"
            ct = "content_type='text/plain'"
    else:
        response_string = "User not found(3)"
        ct = "content_type='text/plain'"
    return HttpResponse(response_string, ct)

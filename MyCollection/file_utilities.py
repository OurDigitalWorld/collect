__author__ = 'walter'
from django.core import serializers
from MyCollection.models import Order, Group, Record


def get_group_thumbnail(groups):
    thumb_list = []
    thumb_group_dict = {}
    for group in groups:
        thumbs = Order.objects.filter(grp=group.id).select_related('rec').order_by('number')
        #if group.id not in thumb_group_dict:
        #print(group.id)
        thumb_group_dict['id'] = group.id
        if thumbs:
            thumb_group_dict['url_thumbnail'] = thumbs[0].rec.url_thumbnail
        else:
            thumb_group_dict['url_thumbnail'] = 'http://images.ourontario.ca/glib/newcollection.gif'
        #print(thumbs[0].rec.url_thumbnail)
        thumb_group_dict['name'] = group.name
        thumb_group_dict['num_recs'] = group.num_recs
        #print(thumb_group_dict)
        thumb_list.append(thumb_group_dict)
        thumb_group_dict = {}
    #print(thumb_list)
    return thumb_list

def get_group_list(record_id, user_id):
    groups = Group.objects.filter(user=user_id).order_by('group_order')
    return_string = "<ul>"
    for group in groups:
        return_string += '<li><input type="checkbox" name="group_id" value="%s' % group.id
        order = Order.objects.filter(grp=group.id, rec=record_id)
        if order:
            return_string += '|%s" checked="checked" ' % order[0].number
        else:
            return_string += '|999"'
        return_string += '>%s</li>' % group.name
    return_string += "</ul>"
    return return_string


def get_unassigned_records_count(user_id):
    non_group_records = get_unassigned_records_list(user_id)
    non_group_record_count = 0  # because a count recs + a list from raw sql is painful
    for rec in non_group_records:
        non_group_record_count += 1
    return non_group_record_count


def get_unassigned_records_list(user_id):
    non_group_records = Record.objects.filter(record_assignment__isnull = True, user_id=user_id)
    return non_group_records
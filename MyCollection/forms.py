__author__ = 'walter'
from django import forms
from django.db.models import Max

from MyCollection.models import Group, Record, Order


class AddGroupForm(forms.ModelForm):
    name = forms.CharField(max_length=256)
    introduction = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Group
        fields = ['name', 'introduction']

    def __init__(self, *args, **kwargs):
        super(AddGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['size'] = 60
        self.fields['introduction'].widget.attrs['rows'] = 8
        self.fields['introduction'].widget.attrs['cols'] = 60
        self.fields['introduction'].widget.attrs['class'] = 'full_text'

    def save(self, request, user_id, *args, **kwargs):
        user_id = int(user_id)
        max_group_order = Group.objects.filter(user=user_id).aggregate(Max('group_order'))
        #print("max_group_order: ", max_group_order)
        group_order = max_group_order['group_order__max']
        #print("group order: ", group_order)
        if group_order:
            group_order = int(group_order) + 1
        else:
            group_order = 1
        groupadd = super(AddGroupForm, self).save(commit=False)
        groupadd.user_id = user_id
        groupadd.name = request.get('name')
        groupadd.introduction = request.get('introduction')
        groupadd.group_order = group_order
        #if request.get('public_display') == 'True':
            # print('pub dis: ', request.get('public_display'))
        #    groupadd.public_display = True
        #else:
        #    groupadd.public_display = False
        groupadd.public_display = False
        groupadd.view = 'single'

        groupadd.save()
        return groupadd


class EditGroupForm(forms.ModelForm):
    id = forms.HiddenInput()
    name = forms.CharField(max_length=256)
    introduction = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'introduction']

    def __init__(self, *args, **kwargs):
        super(EditGroupForm, self).__init__(*args, **kwargs)  # Call to ModelForm constructor
        self.fields['name'].widget.attrs['size'] = 60
        self.fields['introduction'].widget.attrs['rows'] = 8
        self.fields['introduction'].widget.attrs['cols'] = 60
        self.fields['introduction'].widget.attrs['class'] = 'full_text'

    def save(self, request, user_id, group_id, *args, **kwargs):
        group_id = int(group_id)
        groupadd = super(EditGroupForm, self).save(commit=False)
        groupadd.name = request.get('name')
        groupadd.introduction = request.get('introduction')
        if request.get('public_display') == 'False':
            # print('pub dis: ', request.get('public_display'))
            groupadd.public_display = False
        else:
            groupadd.public_display = True
        groupadd.id = group_id
        groupadd.save()


class EditRecordForm(forms.ModelForm):
    id = forms.HiddenInput()
    user_notes = forms.CharField(widget=forms.Textarea(), required=False)
    user_tags = forms.CharField(widget=forms.Textarea(), required=False)
    user_title = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Record
        fields = ['id', 'user_notes', 'user_tags', 'user_title']

    def save(self, request, user_id, record_id, *args, **kwargs):
        """
        handler for form when updating individual record
        :param request: url's request object
        :param record_id: id of the record being acted on
        :param args:
        :param kwargs:
        """
        #print('record_id', record_id)
        record_id = int(record_id)
        recordedit = super(EditRecordForm, self).save(commit=False)
        group_ids = request.getlist('group_id')
        #print("group_ids: ", group_ids)
        recordedit.user_title = self.cleaned_data['user_title']
        recordedit.user_notes = self.cleaned_data['user_notes']
        recordedit.user_tags = self.cleaned_data['user_tags']
        #recordedit.id = record_id
        recordedit.save()
        # flush out existing order objects for this record
        Order.objects.filter(rec=record_id).delete()
        for gid in group_ids:
            grp_id, num = gid.split('|')
            #print('grp_id .. num: ', grp_id, "  ", num)
            if int(num) == 999:
                max_list = Order.objects.filter(grp=grp_id).aggregate(Max('number'))
                max_group_number = max_list.get('number__max')
                #print('max_group_number: ', max_group_number)
                if max_group_number is None:
                    num = 0
                else:
                    num = int(max_group_number) + 1
                #print('rec_id=',record_id, 'grp_id=', grp_id, 'number=',num)
                Order.objects.create(rec_id=record_id, grp_id=grp_id, number=num)
            else:
                Order.objects.create(rec_id=record_id, grp_id=grp_id, number=num)
            #print('finished pass')
        #print('done with EditRecordForm')
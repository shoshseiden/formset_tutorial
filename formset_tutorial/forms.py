from django import forms
from django.forms.formsets import BaseFormSet

class LinkForm(forms.Form):
    """
    Form for individual user links
    """
    anchor = forms.CharField(max_length=100, widgets=forms.TextInput(attrs={
            'placeholder': 'Link Name / Anchor Text',
        }), required=False)
    url = forms.URLField(widgets=forms.URLInput(attrs={
            'placeholder': 'URL',
        }), required=False)


class ProfileForm(forms.Form):
    """
    Form for user to update their own profile details
    (excluding links which are handled by a separate formset)
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.fields['first_name'] = forms.CharField(max_length=30, initial = self.user.first_name,
                                                    widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                    }))
        self.fields['last_name'] = forms.CharField(max_length=30, initial=self.user.last_name,
                                                    widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                    }))


class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        if any(self.errors):
            return

        anchors = []
        urls = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data['anchor']
            url = form.cleaned_data['url']

            # Check that no two links have the same anchor or URL
            if anchor and url:
                if anchor in anchors:
                    duplicates = True
                anchors.append(anchor)

                if url in urls:
                    duplicates = True
                urls.append(url)

            if duplicates:
                raise forms.validationError(
                    'Links must have unique anchors and URLs.',
                    code='duplicate_links'
                )

            # Check that all links have both an anchor and URL
            if url and not anchor:
                raise forms.validationError(
                    'All links must have an anchor.',
                    code='missing_anchor'
                )
            elif anchor and not url:
                raise forms.validationError(
                    'All links must have a URL.',
                    code='missing_URL'
                )

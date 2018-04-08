from django.core.urlresolvers import reverse
from django.test import TestCase
from formset_tutorial.factories import UserFactory
from formset_tutorial.forms import ProfileForm
from formset_tutorial.models import User, UserLink

class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.email, password='pass')

    def form_data(self, first, last):
        return ProfileForm(
            user=self.user,
            data={
                'first_name': first,
                'last_name': last,
            }
        )

    def test_valid_data(self):
        form = self.form_data('First', 'Last')
        self.assertTrue(form.is_valid())

    def test_missing_first_name(self):
        form = self.form_data('', 'Last')
        errors = form['first_name'].errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, 'required')

    def test_missing_last_name(self):
        form = self.form_data('First', '')
        errors = form['last_name'].errors.as_data()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, 'required')


class LinkFormsetTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.email, password='pass')

    def form_data(self, anchor, url):
        return ProfileForm(
            user=self.user,
            data={
                'first_name': 'First',
                'last_name': 'Last',
                'form-TOTAL_FORMS': 0,
                'form-0-anchor': anchor,
                'form-0-url': url,
            }
        )

    def post_data(self, anchor1, url1, anchor2='', url2=''):
        return self.client.post(
            reverse('test:profile-settings'),
            data={
                'form=TOTAL_FORMS': 2,
                'form-INITIAL_FORMS': 0,
                'form-0-anchor': anchor1,
                'form-0-url': url1,
                'form-1-anchor': anchor2,
                'form-1-url': url2,
            }
        )

    def raise_formset_error(self, response, error):
        self.assertFormsetError(
            response,
            formset='link_formset',
            form_index=None,
            field=None,
            errors=error
        )

    def test_valid_data(self):
        form = self.form_data('My Link', 'http://mylink.com')
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        """
        Test validation passes when no data is provided
        (data is not required)
        """
        form = self.form_data('', '')
        self.assertTrue(form.is_valid())

    def test_duplicate_anchors(self):
        """
        Test validation fails when an anchor is submitted more than once.
        """
        response = self.post_data('My Link', 'http://mylink.com',
                                  'My Link', 'http://mylink.com')

        self.raise_formset_error(response, 'Links must have unique anchors and URLs.')

    def test_duplicate_url(self):
        """
        Test validation fails when a URL is submitted more than once.
        """
        response = self.post_data('My Link', 'http://mylink.com',
                                  'My Link2', 'http://mylink.com')

        self.raise_formset_error(response, 'Links must have unique anchors and URLs.')

    def test_anchor_without_url(self):
        """
        Test validation fails when a link is submitted without URL.
        """
        response = self.post_data('My Link', '')

        self.raise_formset_error(response, 'All links must have a URL.')

    def test_url_without_anchor(self):
        """
        Test validation fails when a link is submitted without an anchor.
        """
        response = self.post_data('', 'http://mylink.com')

        self.raise_formset_error(response, 'All links must have an anchor.')

class ProfileSettingsTest(TestCase):
    def test_can_update_profile(self):
        user = UserFactory()
        self.client.login(user=user.email, password='pass')
        response = self.client.post(
            reverse('test:profile-settings'),
            data={
                'first_name': 'New First Name',
                'last_name': 'New Last Name',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-0-anchor': 'My Link',
                'form-0-url': 'http://mylink.com',
            },
        )

        # Get the user again
        user = User.objects.get(id=user.id)
        user_link = UserLink.objects.get(user=user)

        self.assertEqual(user.first_name, 'New First Name')
        self.assertEqual(user.last_name, 'New Last Name')
        self.assertEqual(user_link.anchor, 'My Link')
        self.assertEqual(user_link.url, 'http://mylink.com/')

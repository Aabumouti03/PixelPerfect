from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.contrib.auth import get_user_model
from client.models import Program, Module
from users.admin import (
    CustomUserAdmin, AdminProfileAdmin, EndUserAdmin,
    UserProgramEnrollmentAdmin, UserModuleEnrollmentAdmin,
    UserProgramProgressAdmin, UserModuleProgressAdmin,
    QuestionnaireUserResponseAdmin, QuestionResponseAdmin,
    StickyNoteAdmin, UserResponseAdmin, JournalEntryAdmin
)
from users.models import (
    User, Admin, EndUser, UserProgramEnrollment, UserModuleEnrollment,
    UserProgramProgress, UserModuleProgress, Questionnaire_UserResponse,
    QuestionResponse, StickyNote, UserResponse, JournalEntry
)
from django import forms
from django.contrib import admin

class MockRequest:
    pass

class AdminTests(TestCase):
    """Test Django Admin configurations"""
    
    @classmethod
    def setUpTestData(cls):
        cls.site = AdminSite()
        cls.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        cls.admin_user = get_user_model().objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.user, age=25, gender='M')
        cls.program = Program.objects.create(title='Test Program')
        cls.module = Module.objects.create(title='Test Module')

    def test_custom_user_admin(self):
        admin = CustomUserAdmin(User, self.site)
        self.assertEqual(admin.list_display, ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser'))
        self.assertIn('username', admin.search_fields)

    def test_end_user_admin(self):
        admin = EndUserAdmin(EndUser, self.site)
        self.assertIn('gender', admin.list_filter)

    def test_user_program_enrollment_admin(self):
        admin = UserProgramEnrollmentAdmin(UserProgramEnrollment, self.site)
        self.assertIn('program', admin.list_filter)

    def test_user_module_enrollment_admin(self):
        admin = UserModuleEnrollmentAdmin(UserModuleEnrollment, self.site)
        self.assertIn('module', admin.list_filter)

    def test_questionnaire_user_response_admin(self):
        admin = QuestionnaireUserResponseAdmin(Questionnaire_UserResponse, self.site)
        self.assertIn('completed_at', admin.list_filter)

    def test_journal_entry_admin(self):
        admin = JournalEntryAdmin(JournalEntry, self.site)
        self.assertIn('date', admin.list_filter)

    def test_sticky_note_admin(self):
        admin = StickyNoteAdmin(StickyNote, self.site)
        self.assertIn('created_at', admin.list_filter)
        self.assertIn('content', admin.search_fields)

    def test_sticky_note_admin_form_queryset(self):
        admin = StickyNoteAdmin(StickyNote, self.site)
        form = admin.get_form(MockRequest())
        self.assertEqual(list(form.base_fields['user'].queryset), list(EndUser.objects.all()))

    def test_user_response_admin(self):
        admin = UserResponseAdmin(UserResponse, self.site)
        self.assertIn('user', admin.list_display)
        self.assertIn('question', admin.list_display)
        self.assertIn('response_text', admin.list_display)
        self.assertIn('user__user__username', admin.search_fields)
        self.assertIn('question__question_text', admin.search_fields)

    def test_user_response_admin_form_queryset(self):
        admin = UserResponseAdmin(UserResponse, self.site)
        form = admin.get_form(MockRequest())
        self.assertEqual(list(form.base_fields['user'].queryset), list(EndUser.objects.all()))

    def test_journal_entry_unregistration(self):
        if admin.site.is_registered(JournalEntry):
            admin.site.unregister(JournalEntry)
        self.assertFalse(admin.site.is_registered(JournalEntry))
        admin.site.register(JournalEntry, JournalEntryAdmin)
        self.assertTrue(admin.site.is_registered(JournalEntry))

    def test_sticky_note_admin_get_form(self):
        """Ensure StickyNoteAdmin limits user selection to EndUsers"""
        admin = StickyNoteAdmin(StickyNote, self.site)
        form = admin.get_form(MockRequest())
        self.assertEqual(list(form.base_fields['user'].queryset), list(EndUser.objects.all()))

    def test_user_response_admin_get_form(self):
        """Ensure UserResponseAdmin limits user selection to EndUsers"""
        admin = UserResponseAdmin(UserResponse, self.site)
        form = admin.get_form(MockRequest())
        self.assertEqual(list(form.base_fields['user'].queryset), list(EndUser.objects.all()))
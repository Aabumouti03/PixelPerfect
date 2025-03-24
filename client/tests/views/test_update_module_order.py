import json
from django.test import TestCase
from django.urls import reverse
from client.models import Program, Module, ProgramModule

class UpdateModuleOrderTest(TestCase):
    
    def setUp(self):
        """Set up a program, dummy modules, and their ProgramModule entries for testing."""
        self.program = Program.objects.create(
            title="Test Program", description="Program for module ordering test"
        )
        self.dummy_module1 = Module.objects.create(title="Module 1", description="Dummy module 1")
        self.dummy_module2 = Module.objects.create(title="Module 2", description="Dummy module 2")
        self.dummy_module3 = Module.objects.create(title="Module 3", description="Dummy module 3")
        
        self.pm1 = ProgramModule.objects.create(
            program=self.program, module=self.dummy_module1, order=1
        )
        self.pm2 = ProgramModule.objects.create(
            program=self.program, module=self.dummy_module2, order=2
        )
        self.pm3 = ProgramModule.objects.create(
            program=self.program, module=self.dummy_module3, order=3
        )
        self.url = reverse("update_module_order", args=[self.program.id])

    def test_update_module_order_successfully(self):
        """Test that the module order is updated successfully."""
        payload = {
            "order": [
                {"id": self.pm2.id},
                {"id": self.pm3.id},
                {"id": self.pm1.id}
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"), msg="Expected a success response when updating order.")

        self.pm1.refresh_from_db()
        self.pm2.refresh_from_db()
        self.pm3.refresh_from_db()

        self.assertEqual(self.pm2.order, 1)
        self.assertEqual(self.pm3.order, 2)
        self.assertEqual(self.pm1.order, 3)

    def test_update_module_order_invalid_json(self):
        """Test that sending invalid JSON data returns an error response."""
        response = self.client.post(
            self.url,
            data="invalid json",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data.get("success"))
        self.assertIn("error", data)

    def test_update_module_order_missing_order_key(self):
        """Test that missing the 'order' key in payload returns an error."""
        payload = {"not_order": []}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data.get("success"))
        self.assertIn("error", data)

    def test_update_module_order_program_not_found(self):
        """Test that updating a non-existent program returns a 404."""
        non_existent_url = reverse("update_module_order", args=[999999])
        payload = {
            "order": [
                {"id": self.pm1.id},
                {"id": self.pm2.id},
                {"id": self.pm3.id}
            ]
        }
        response = self.client.post(
            non_existent_url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

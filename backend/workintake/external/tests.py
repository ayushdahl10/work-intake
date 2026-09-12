from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from external.models import Status, WorkItem

# Create your tests here.


@override_settings(AI_PROVIDER="mock")
class WorkItemTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_duplicate_external_id(self):
        payload = {
            "external_id": "XD-123",
            "title": "File Upload Error",
            "description": "File upload failed with error code abc-1",
        }
        url = "/api/create-work-item"
        res1 = self.client.post(url, payload, format="json")
        self.assertEqual(res1.status_code, 201)
        res2 = self.client.post(url, payload, format="json")
        self.assertEqual(res2.status_code, 409)
        self.assertEqual(WorkItem.objects.filter(external_id="XD-123").count(), 1)

    @patch("external.apis.apis.worker.submit")
    def test_received_item_preserves_after_failure(self, mock_worker):
        payload = {
            "external_id": "XD-1234",
            "title": "fail",
            "description": "check fail test",
        }
        url = "/api/create-work-item"
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, 201)
        work_instance = WorkItem.objects.get(external_id="XD-1234")
        from external.services import analysis_in_background

        analysis_in_background(work_instance.pk)
        work_instance.refresh_from_db()
        self.assertEqual(work_instance.retryCount, 0)
        self.assertEqual(work_instance.status, "FAILED")
        self.assertIsNotNone(work_instance.analysisError)

    @patch("external.apis.apis.worker.submit")
    def test_retry_work_item(self, mock_worker):
        work_item = WorkItem.objects.create(
            external_id="XD-12345",
            title="retry test",
            description="retry test",
            status="FAILED",
            analysisError="500 Error while analyzing work item",
            retryCount=0,
        )
        url = f"/api/work-item/{work_item.uid}/trigger"
        res = self.client.patch(url, format="json")
        self.assertEqual(res.status_code, 202)
        from external.services import analysis_in_background

        analysis_in_background(work_item.pk)
        work_item.refresh_from_db()
        print("work_item.retryCount", work_item.retryCount)
        self.assertEqual(work_item.retryCount, 1)
        self.assertEqual(work_item.status, "READY_FOR_REVIEW")
        self.assertIsNotNone(work_item.analysisResult)
        self.assertIsNone(work_item.analysisError)

    def test_invalid_transaction(self):
        instance = WorkItem.objects.create(
            external_id="XDX-123",
            title="invalid transaction",
            description="invalid transaction",
            status="COMPLETED",
            analysisError="500 Error while analyzing work item",
            retryCount=0,
            analysisResult={
                "category": "Bug Report",
                "priority": "HIGH",
                "summary": "Mock AI Service analyzed work item",
                "recommendedAction": "Mock AI Service recommended next action",
            },
        )

        url = f"/api/work-item/{instance.uid}/trigger"
        res = self.client.patch(url, format="json")
        self.assertEqual(res.status_code, 404)
        instance.refresh_from_db()

        # Test transition to method
        if instance.check_transition_to(Status.RECEIVED):
            instance.status = Status.RECEIVED
            instance.save()
        instance.refresh_from_db()
        self.assertNotEqual(instance.status, Status.RECEIVED)

    def test_work_create_payload(self):
        #missing title 
        payload = {
            "external_id": "XD-1234",
            "description": "check fail test",
        }
        url = "/api/create-work-item"
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(WorkItem.objects.filter(external_id="XD-1234").count(), 0)

        #missing description
        payload = {
            "external_id": "XD-1234",
            "title": "fail",
        }
        url = "/api/create-work-item"
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(WorkItem.objects.filter(external_id="XD-1234").count(), 0)

        #missing external_id
        payload = {
            "title": "fail",
            "description": "check fail test",
        }
        url = "/api/create-work-item"
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(WorkItem.objects.filter(external_id="XD-1234").count(), 0)

        